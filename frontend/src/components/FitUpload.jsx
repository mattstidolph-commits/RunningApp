import { useRef, useState } from 'react'
import { uploadFit } from '../api'

export default function FitUpload({ onUploaded }) {
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState(null)
  const inputRef = useRef()

  const handleFiles = async (files) => {
    for (const file of files) {
      if (!file.name.endsWith('.fit')) { setMessage('Only .fit files accepted'); continue }
      setUploading(true)
      setMessage(null)
      try {
        await uploadFit(file)
        setMessage(`Imported: ${file.name}`)
        onUploaded?.()
      } catch (e) {
        setMessage(e.response?.data?.detail === 'Activity already imported'
          ? `${file.name}: already imported`
          : `${file.name}: upload failed`)
      } finally {
        setUploading(false)
      }
    }
  }

  const onDrop = (e) => { e.preventDefault(); handleFiles(e.dataTransfer.files) }
  const onDragOver = (e) => e.preventDefault()

  return (
    <div>
      <div
        onDrop={onDrop} onDragOver={onDragOver}
        onClick={() => inputRef.current.click()}
        className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors"
      >
        <p className="text-gray-500 text-sm">{uploading ? 'Importing...' : 'Drop .fit files here, or click to select'}</p>
        <input ref={inputRef} type="file" accept=".fit" multiple className="hidden"
          onChange={e => handleFiles(e.target.files)} />
      </div>
      {message && <p className="mt-2 text-sm text-gray-600">{message}</p>}
    </div>
  )
}
