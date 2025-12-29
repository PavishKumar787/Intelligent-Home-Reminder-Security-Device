import React, { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon, Loader2, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface UploadFormProps {
  title: string;
  description?: string;
  nameLabel?: string;
  namePlaceholder?: string;
  buttonText?: string;
  onSubmit: (name: string, file: File) => Promise<void>;
  existingNames?: string[];
  isReEnroll?: boolean;
  className?: string;
}

const UploadForm: React.FC<UploadFormProps> = ({
  title,
  description,
  nameLabel = 'Name',
  namePlaceholder = 'Enter name',
  buttonText = 'Submit',
  onSubmit,
  existingNames = [],
  isReEnroll = false,
  className,
}) => {
  const [name, setName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (selectedFile: File | null) => {
    if (selectedFile && selectedFile.type.startsWith('image/')) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileChange(e.dataTransfer.files[0]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim() || !file) return;

    try {
      setIsLoading(true);
      setIsSuccess(false);

      await onSubmit(name.trim(), file);

      setIsSuccess(true);
      setName('');
      setFile(null);
      setPreview(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className={cn('glass-card rounded-xl p-6 border border-border', className)}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-1">{title}</h3>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="name">{nameLabel}</Label>

          {isReEnroll && existingNames.length > 0 ? (
            <select
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
              required
            >
              <option value="">Select a user</option>
              {existingNames.map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          ) : (
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={namePlaceholder}
              required
            />
          )}
        </div>

        <div className="space-y-2">
          <Label>Face Image</Label>

          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={cn(
              'relative border-2 border-dashed rounded-xl p-8 cursor-pointer',
              isDragOver ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50',
              preview && 'p-4'
            )}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
            />

            {preview ? (
              <div className="relative">
                <img src={preview} className="max-h-48 mx-auto rounded-lg" />
                <Button
                  type="button"
                  variant="destructive"
                  size="icon"
                  className="absolute -top-2 -right-2"
                  onClick={(e) => { e.stopPropagation(); clearFile(); }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <div className="text-center">
                <Upload className="h-6 w-6 mx-auto text-primary mb-2" />
                <p className="text-sm font-medium">Drop an image or click to browse</p>
                <p className="text-xs text-muted-foreground">PNG, JPG</p>
              </div>
            )}
          </div>
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={!name || !file || isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Processing...
            </>
          ) : isSuccess ? (
            <>
              <CheckCircle className="h-4 w-4" /> Success!
            </>
          ) : (
            <>
              <ImageIcon className="h-4 w-4" /> {buttonText}
            </>
          )}
        </Button>
      </form>
    </div>
  );
};

export default UploadForm;
