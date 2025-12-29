import React from 'react';
import { UserPlus } from 'lucide-react';
import UploadForm from '@/components/shared/UploadForm';
import { faceApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

const EnrollPage: React.FC = () => {
  const { toast } = useToast();

  const handleEnroll = async (name: string, file: File) => {
    try {
      await faceApi.enrollFace({ name, image: file });
      toast({
        title: 'Face Enrolled Successfully',
        description: `${name}'s face has been added to the system.`,
      });
      // 🔥 Note: If you navigate to ReEnrollPage after this, 
      // the users list will be refreshed there automatically
    } catch (error) {
      toast({
        title: 'Enrollment Failed',
        description: 'There was an error enrolling the face. Please try again.',
        variant: 'destructive',
      });
      throw error;
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-primary/10 mb-4">
          <UserPlus className="h-7 w-7 text-primary" />
        </div>
        <h1 className="text-2xl font-bold mb-2">Enroll New Face</h1>
        <p className="text-muted-foreground">
          Add a new person to the face recognition database
        </p>
      </div>

      <UploadForm
        title="Face Enrollment"
        description="Upload a clear photo of the person's face for enrollment. Ensure good lighting and a frontal view."
        nameLabel="Person's Name"
        namePlaceholder="Enter the person's name"
        buttonText="Enroll Face"
        onSubmit={handleEnroll}
      />

      <div className="glass-card rounded-xl p-5 border border-border">
        <h3 className="font-semibold mb-3">Tips for Best Results</h3>
        <ul className="space-y-2 text-sm text-muted-foreground">
          <li className="flex items-start gap-2">
            <span className="text-primary">•</span>
            Use a well-lit photo with the face clearly visible
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary">•</span>
            Ensure the face is frontal and not at an angle
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary">•</span>
            Avoid photos with sunglasses or face coverings
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary">•</span>
            Higher resolution photos provide better recognition
          </li>
        </ul>
      </div>
    </div>
  );
};

export default EnrollPage;
