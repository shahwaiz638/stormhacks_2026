import { useEffect, useRef, useState } from 'react'
import { ImagePlus, Plus, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

function PhotoPreview({ file }) {
  const image = useRef(null)
  useEffect(() => {
    const objectUrl = URL.createObjectURL(file)
    image.current.src = objectUrl
    return () => URL.revokeObjectURL(objectUrl)
  }, [file])
  return <img ref={image} alt={file.name} className="h-24 w-full rounded-md bg-muted object-cover" />
}

function PhotoUpload({ files, onChange, disabled = false }) {
  const input = useRef(null)
  const dragDepth = useRef(0)
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState('')

  function addFiles(incoming) {
    if (disabled) return
    const images = Array.from(incoming).filter((file) => file.type.startsWith('image/'))
    setError(images.length < incoming.length ? 'Only image files can be added.' : '')
    const next = [...files]
    for (const image of images) {
      if (!next.some((file) => file.name === image.name && file.size === image.size && file.lastModified === image.lastModified)) next.push(image)
    }
    onChange(next)
  }

  return (
    <div className="space-y-3">
      <input ref={input} id="found-photos" type="file" accept="image/*" multiple disabled={disabled} className="hidden" onChange={(event) => { addFiles(event.target.files); event.target.value = '' }} />
      <button
        type="button"
        disabled={disabled}
        aria-label={files.length ? 'Add more photos' : 'Upload photos of the found item'}
        aria-describedby="found-photo-note"
        onClick={() => input.current?.click()}
        onDragEnter={(event) => { event.preventDefault(); if (!disabled) { dragDepth.current++; setIsDragging(true) } }}
        onDragOver={(event) => { event.preventDefault(); event.dataTransfer.dropEffect = disabled ? 'none' : 'copy' }}
        onDragLeave={(event) => { event.preventDefault(); dragDepth.current = Math.max(0, dragDepth.current - 1); if (!dragDepth.current) setIsDragging(false) }}
        onDrop={(event) => { event.preventDefault(); dragDepth.current = 0; setIsDragging(false); addFiles(event.dataTransfer.files) }}
        className={cn('flex w-full flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed border-input bg-muted/20 px-5 text-center transition-colors hover:border-muted-foreground hover:bg-muted/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50', files.length ? 'min-h-24 py-5' : 'min-h-52 py-8', isDragging && 'border-primary bg-muted/60')}
      >
        {files.length ? <Plus className="size-5 text-muted-foreground" aria-hidden="true" /> : <ImagePlus className="size-8 text-muted-foreground" aria-hidden="true" />}
        <span className="text-sm font-medium">{isDragging ? 'Drop photos here' : files.length ? 'Add more photos' : 'Drag photos here or click to browse'}</span>
        {!files.length && <span className="text-xs text-muted-foreground">You can choose multiple photos.</span>}
      </button>
      {files.length > 0 && (
        <ul aria-label="Selected photos" className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {files.map((file, index) => (
            <li key={`${file.name}-${file.size}-${file.lastModified}`} className="relative min-w-0 rounded-lg border border-border p-2">
              <PhotoPreview file={file} />
              <p className="mt-2 truncate text-xs text-muted-foreground" title={file.name}>{file.name}</p>
              <Button type="button" variant="secondary" size="icon" disabled={disabled} aria-label={`Remove ${file.name}`} className="absolute right-3 top-3 size-6" onClick={() => onChange(files.filter((_, position) => position !== index))}><X className="size-3" /></Button>
            </li>
          ))}
        </ul>
      )}
      <p id="found-photo-note" className="text-xs text-muted-foreground">Photos are attached when you submit your report.</p>
      <p role="status" className="text-xs text-red-400">{error}</p>
    </div>
  )
}

export default PhotoUpload
