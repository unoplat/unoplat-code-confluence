import React, { useState } from 'react';
import { Link } from '@tanstack/react-router';
import GitHubTokenPopup from '../components/GitHubTokenPopup';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Github, ExternalLink } from 'lucide-react';

export default function SettingsPage(): React.ReactElement {
  const [showTokenPopup, setShowTokenPopup] = useState<boolean>(false);
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
      
      <Card>
        <CardContent className="space-y-6 pt-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">GitHub Repositories</h3>
                <p className="text-sm text-muted-foreground">
                  Add or manage GitHub repositories for ingestion.
                </p>
              </div>
              <Button asChild variant="outline">
                <Link to="/onboarding" className="flex items-center gap-2">
                  <span>Go to Onboarding</span>
                  <ExternalLink className="h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
          
          <div className="space-y-2 pt-2 border-t">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">GitHub Authentication</h3>
                <p className="text-sm text-muted-foreground">
                  Update or change your GitHub Personal Access Token.
                </p>
              </div>
              <Button 
                variant="outline" 
                onClick={() => setShowTokenPopup(true)}
                className="flex items-center gap-2"
              >
                <Github className="h-4 w-4" />
                <span>Manage Token</span>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* GitHub Token Popup */}
      <GitHubTokenPopup 
        open={showTokenPopup} 
        onClose={() => setShowTokenPopup(false)}
        isUpdate={true}
        onSuccess={() => {
          alert('Token updated successfully!');
        }}
      />
    </div>
  );
} 