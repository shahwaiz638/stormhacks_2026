"""Interactive LostLens API demo. Run: python demo.py

Uses the real HTTP endpoints, Gemini, and TiDB. Only FOUND submissions are saved.
Starts a local backend if needed, and stops only the server it started.
No API keys or database credentials are handled by this demo.
"""

import argparse
import base64
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

MAX_IMAGE_BYTES = 5 * 1024 * 1024


class DemoError(Exception):
    pass


def api(base_url, path, method="GET", payload=None, timeout=180):
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(base_url + path, data=body, method=method,
                      headers={"Content-Type": "application/json"} if body else {})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as exc:
        try:
            detail = json.load(exc).get("detail", "Request failed")
        except (ValueError, UnicodeDecodeError):
            detail = "Backend returned an unexpected error response"
        raise DemoError(f"HTTP {exc.code}: {json.dumps(detail, ensure_ascii=False)}") from None
    except (URLError, TimeoutError, OSError):
        message = "Could not reach the backend, or the request timed out."
        if method == "POST":
            message += " It may have been saved: check Browse before submitting again."
        raise DemoError(message) from None
    except (ValueError, UnicodeDecodeError):
        raise DemoError("Backend returned invalid JSON") from None


def ensure_server(base_url):
    """Reuse a running API, or start this folder's backend on a loopback address."""
    def ready():
        try:
            return api(base_url, "/health", timeout=1).get("status") == "ok"
        except DemoError:
            return False

    if ready():
        print("Connected to the running backend.")
        return None
    url = urlsplit(base_url)
    if url.scheme != "http" or url.hostname not in ("127.0.0.1", "localhost"):
        raise DemoError("Start the backend at the specified URL, then run the demo again.")
    print("Starting FastAPI locally...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0",
         "--port", str(url.port or 80)],
        cwd=Path(__file__).resolve().parent,
        stdout=subprocess.DEVNULL,
    )
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise DemoError("Backend startup failed. Check the server output above.")
            if ready():
                return process
            time.sleep(0.1)
        raise DemoError("Backend startup timed out.")
    except BaseException:
        stop_server(process)
        raise


def stop_server(process):
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def ask(label, default=None):
    value = input(f"{label}" + (f" [{default}]" if default is not None else "") + ": ").strip()
    return value or default or ""


def compact(value):
    """Show actual API JSON without flooding the terminal with Base64 photos."""
    if isinstance(value, dict):
        return {key: compact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [compact(item) for item in value]
    if isinstance(value, str) and value.startswith("data:image/"):
        return f"<stored image data URL: {len(value):,} characters>"
    return value


def show_json(value):
    print(json.dumps(compact(value), indent=2, ensure_ascii=False))


def show_matches(matches):
    if not matches:
        print("No FOUND candidates returned. Submit a FOUND report first.")
        return
    for number, match in enumerate(matches, 1):
        print(f"\n{number}. {match['title']} ({match['candidate_id']})")
        print(f"   Location: {match.get('location_name')}")
        print(f"   Vector similarity: {match['vector_score']:.4f} "
              f"(display score {match['match_percentage']}%, not a probability)")
        if match.get("ai_match_percentage") is not None:
            print(f"   Gemini estimate: {match['ai_match_percentage']}% (subjective)")
        for reason in match.get("matching_reasons", []):
            print(f"   - {reason}")
        print(f"   {match.get('summary_explanation', '')}")


def submit_report(base_url, kind):
    print(f"\n{kind.upper()}: " + ("saved to TiDB" if kind == "found" else "read-only search; nothing is saved"))
    print("For a vision check, attach a real photo and use a neutral description")
    print("such as 'Please identify the item in this photo'.")
    payload = {
        "title": ask("Title", "Demo item"),
        "description": ask("Description"),
        "location_name": ask("Location (maximum 100 characters)", "SFU Library"),
        "event_timestamp": ask("Event time (ISO format with offset)",
            datetime.now().astimezone().isoformat(timespec="seconds")),
    }
    image_path = ask("Photo path (JPEG/PNG/WebP; Enter to skip)")
    if kind == "found" and not image_path:
        raise DemoError("A photo is required for a FOUND report")
    if image_path:
        path = Path(image_path.strip('"').strip("'")).expanduser()
        try:
            with path.open("rb") as image:
                data = image.read(MAX_IMAGE_BYTES + 1)
        except OSError:
            raise DemoError("Cannot read that photo path") from None
        if not data or len(data) > MAX_IMAGE_BYTES:
            raise DemoError("Photo must be nonempty and at most 5 MiB")
        # Raw Base64 is supported; the backend detects/verifies the image type.
        payload["image_base64"] = base64.b64encode(data).decode("ascii")
        print(f"Photo attached: {path.name} ({len(data):,} bytes)")
    print("\nSending to FastAPI. Waiting for live Gemini extraction, a text embedding,")
    print("and FOUND-only search with Gemini selecting up to two matches..." if kind == "lost" else "and TiDB storage...")
    result = api(base_url, f"/reports/{kind}", "POST", payload)
    report_id = result["report_id"]
    print("\nSearch complete; no lost report was saved." if kind == "lost" else f"\nSAVED: FOUND report {report_id}")
    print("Gemini-extracted attributes:")
    show_json(result["attributes"])
    for warning in result.get("warnings", []):
        print("WARNING:", warning)
    if kind == "lost":
        show_matches(result.get("matches", []))
        return None
    print("\nVerifying persistence through GET /reports/{id}...")
    try:
        stored = api(base_url, "/reports/" + quote(report_id, safe=""))
        if stored.get("id") != report_id:
            raise DemoError("Read-back returned a different report ID")
        print("PASS: the saved report was read back from TiDB.")
        if payload.get("image_base64"):
            print("Stored display photo:", "present" if stored.get("image_url") else "missing")
    except DemoError as exc:
        print(f"Report was saved, but read-back verification failed: {exc}")
    return report_id


def explain():
    print("""
This demo calls the same HTTP API that React will call. No mocked AI responses.

1. FastAPI validates the report and verifies/decodes the optional photo.
2. services.extract_item_attributes sends text plus image bytes to Gemini.
   The system prompt requests category, color, brand, model, features and keywords;
   user text/images are treated as untrusted data. Output is schema-validated.
3. services.generate_embedding turns the description and extracted attributes
   into a text-only vector of exactly 768 dimensions.
4. FOUND reports are saved to TiDB; LOST submissions never insert/update a row.
5. LOST reports search the closest five FOUND reports using cosine distance.
6. Gemini rejects incompatible item types and selects up to two plausible matches.

A successful FOUND submission proves extraction, embedding and storage completed.
A successful LOST search proves retrieval and Gemini evaluation completed.
/health alone checks that FastAPI is running, not Gemini or TiDB connectivity.
AI identification and match scores are estimates, not guarantees of correctness.
The actual prompts and model configuration are in services.py.
""")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="FastAPI base URL")
    args = parser.parse_args()
    base_url = args.url.rstrip("/")
    url = urlsplit(base_url)
    if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password:
        parser.error("--url must be an HTTP(S) backend URL without credentials")
    process = None
    last_id = None
    try:
        print("LostLens live API demo")
        print("Real Gemini calls. FOUND reports are saved; LOST searches are read-only. Nothing is deleted.")
        process = ensure_server(base_url)
        print(f"API: {base_url} | Docs: {base_url}/docs")
        while True:
            print("\n1 Submit FOUND   2 Submit LOST   3 Browse FOUND")
            print("4 Read report    5 Recheck matches   6 Explain Gemini flow   0 Exit")
            choice = ask("Choose")
            try:
                if choice == "0":
                    break
                if choice in ("1", "2"):
                    last_id = submit_report(base_url, "found" if choice == "1" else "lost") or last_id
                elif choice == "3":
                    rows = api(base_url, "/reports?type=FOUND&limit=20")
                    print(f"\n{len(rows)} FOUND reports (up to 20):")
                    for row in rows:
                        print(f"{row['id']} | {row['title']} | {row.get('location_name')}")
                elif choice in ("4", "5"):
                    report_id = ask("Report ID (use a LOST ID for matches)", last_id)
                    path = "/reports/" + quote(report_id, safe="")
                    result = api(base_url, path + ("/matches" if choice == "5" else ""))
                    if choice == "4":
                        show_json(result)
                    else:
                        show_matches(result["matches"])
                        for warning in result.get("warnings", []):
                            print("WARNING:", warning)
                elif choice == "6":
                    explain()
                else:
                    print("Choose a number from 0 to 6.")
            except DemoError as exc:
                print("\nFAILED:", exc)
    except DemoError as exc:
        print("FAILED:", exc)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nExiting demo.")
    finally:
        stop_server(process)
    return 0


if __name__ == "__main__":
    sys.exit(main())
