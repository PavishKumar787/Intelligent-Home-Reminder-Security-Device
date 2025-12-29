import React, { useState, useEffect } from 'react';
import { RefreshCw, Trash2 } from 'lucide-react';
import UploadForm from '@/components/shared/UploadForm';
import { faceApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';

const ReEnrollPage: React.FC = () => {
  const { toast } = useToast();
  const [existingUsers, setExistingUsers] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const users = await faceApi.getUsers();
      setExistingUsers(users);
    } catch (error) {
      toast({
        title: 'Failed to Load Users',
        description: 'Could not fetch the list of enrolled users.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleReEnroll = async (name: string, file: File) => {
    try {
      await faceApi.reEnrollFace({ name, image: file });
      toast({
        title: 'Face Updated Successfully',
        description: `${name}'s face data has been updated.`,
      });
      await fetchUsers(); // 🔥 Refresh users list after re-enrollment
    } catch (error) {
      toast({
        title: 'Update Failed',
        description: 'There was an error updating the face. Please try again.',
        variant: 'destructive',
      });
      throw error;
    }
  };

  const handleDeleteUser = async (name: string) => {
    if (!confirm(`Are you sure you want to delete ${name}?`)) {
      return;
    }

    try {
      await faceApi.deleteUser(name);
      toast({
        title: 'User Deleted',
        description: `${name} has been removed from the system.`,
      });
      await fetchUsers(); // 🔥 Refresh users list after deletion
    } catch (error) {
      toast({
        title: 'Delete Failed',
        description: 'There was an error deleting the user. Please try again.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-accent/10 mb-4">
          <RefreshCw className="h-7 w-7 text-accent" />
        </div>
        <h1 className="text-2xl font-bold mb-2">Re-Enroll Face</h1>
        <p className="text-muted-foreground">
          Update an existing person's face data in the system
        </p>
      </div>

      <UploadForm
        title="Update Face Data"
        description="Select an existing user and upload a new photo to update their face recognition data."
        nameLabel="Select User"
        buttonText="Update Face"
        onSubmit={handleReEnroll}
        existingNames={existingUsers}
        isReEnroll={true}
      />

      {/* Enrolled Users List with Delete Buttons */}
      <div className="glass-card rounded-xl p-5 border border-border">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Enrolled Users</h3>
          <button
            onClick={fetchUsers}
            disabled={loading}
            className="text-accent hover:text-accent/80 disabled:opacity-50"
            title="Refresh users list"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>

        {existingUsers.length === 0 ? (
          <p className="text-muted-foreground text-sm">No users enrolled yet.</p>
        ) : (
          <div className="space-y-2">
            {existingUsers.map((name) => (
              <div
                key={name}
                className="flex items-center justify-between p-3 border rounded bg-background/50 hover:bg-background transition"
              >
                <span className="font-medium">{name}</span>
                <button
                  onClick={() => handleDeleteUser(name)}
                  className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 p-2 rounded transition"
                  title={`Delete ${name}`}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="glass-card rounded-xl p-5 border border-border">
        <h3 className="font-semibold mb-3">When to Re-Enroll</h3>
        <ul className="space-y-2 text-sm text-muted-foreground">
          <li className="flex items-start gap-2">
            <span className="text-accent">•</span>
            Person is not being recognized consistently
          </li>
          <li className="flex items-start gap-2">
            <span className="text-accent">•</span>
            Significant change in appearance (haircut, glasses, etc.)
          </li>
          <li className="flex items-start gap-2">
            <span className="text-accent">•</span>
            Original enrollment photo was low quality
          </li>
          <li className="flex items-start gap-2">
            <span className="text-accent">•</span>
            To improve recognition accuracy with a better photo
          </li>
        </ul>
      </div>
    </div>
  );
};

export default ReEnrollPage;
