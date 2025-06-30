import React, { useRef, useState, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "../components/ui/alert";
import { AlertCircle } from "lucide-react";
import {
  RepositoryDataTable,
  type RepositoryDataTableRef,
} from "../components/custom/RepositoryDataTable";
import GitHubTokenPopup from "../components/custom/GitHubTokenPopup";
import { LocalRepoOnboardingForm } from "../components/custom/LocalRepoOnboardingForm";
import { useAuthStore } from "@/stores/useAuthStore";
import { useAuthData } from "@/hooks/use-auth-data";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { StatusBadge } from "@/components/custom/StatusBadge";

export default function OnboardingPage(): React.ReactElement {
  console.log("[OnboardingPage] Rendering OnboardingPage component");

  const queryClient = useQueryClient();
  const dataTableRef = useRef<RepositoryDataTableRef>(null);

  // Use useAuthData hook to fetch token status and user data
  const { tokenQuery } = useAuthData();
  // Local control for token popup open/close
  const [isPopupOpen, setIsPopupOpen] = useState<boolean>(false);
  // Track whether we've auto-opened already to avoid re-opening on manual close
  const autoOpenRef = useRef<boolean>(false);
  // Auto-open the popup once when token status is known and no token exists
  useEffect(() => {
    if (
      !autoOpenRef.current &&
      tokenQuery.isSuccess &&
      !tokenQuery.data?.status &&
      tokenQuery.data.errorCode !== 503
    ) {
      autoOpenRef.current = true;
      setIsPopupOpen(true);
    }
  }, [
    tokenQuery.isSuccess,
    tokenQuery.data?.status,
    tokenQuery.data?.errorCode,
  ]);
  const showTokenPopup = isPopupOpen;

  console.log("[OnboardingPage] State: showTokenPopup =", showTokenPopup);

  // Use Zustand store for auth state
  const tokenStatus = useAuthStore((state) => state.tokenStatus);

  const handleTokenSuccess = async (): Promise<void> => {
    console.log("[OnboardingPage] Token submitted successfully");

    console.log(
      "[OnboardingPage] Invalidating repositories query after token submission",
    );
    // Since token status is now handled by Zustand, we only need to invalidate repositories
    await queryClient.invalidateQueries({ queryKey: ["repositories"] });
  };

  console.log(
    "[OnboardingPage] Rendering UI with tokenStatus:",
    tokenStatus?.status,
  );
  return (
    <div className="container mx-auto max-w-7xl px-4 py-8 space-y-8">
      <Tabs defaultValue="github" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="github">GitHub Repository</TabsTrigger>
          <TabsTrigger value="local" className="flex items-center gap-2">
            Local Repository
            <StatusBadge status="alpha" size="sm" />
          </TabsTrigger>
        </TabsList>

        <TabsContent value="github">
          <Card variant="default" padding="lg" radius="lg">
            <CardHeader>
              <CardTitle>GitHub Repositories</CardTitle>
              <CardDescription>
                Connect your GitHub repositories to Unoplat Code Confluence to
                unlock deeper code insights. Browse the repositories below,
                click "Ingest Repo" in the row actions, fill in the required
                details, and submit to begin ingestion.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {tokenStatus &&
                !tokenStatus.status &&
                !showTokenPopup &&
                tokenStatus.errorCode !== 503 && (
                  <Alert
                    variant="warning"
                    size="default"
                    radius="default"
                    className="mb-6"
                  >
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>GitHub Token Required</AlertTitle>
                    <AlertDescription className="mt-2">
                      You need to provide a GitHub token to access your
                      repositories.
                      <div className="mt-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            console.log(
                              '[OnboardingPage] "Set up GitHub Token" button clicked',
                            );
                            setIsPopupOpen(true);
                          }}
                        >
                          Set up GitHub Token
                        </Button>
                      </div>
                    </AlertDescription>
                  </Alert>
                )}

              {tokenStatus?.errorCode === 503 && (
                <Alert
                  variant="destructive"
                  size="default"
                  radius="default"
                  className="mb-6"
                >
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Connection Error</AlertTitle>
                  <AlertDescription>
                    Could not connect to the server. Please refresh the page.
                  </AlertDescription>
                </Alert>
              )}

              {tokenStatus?.status && (
                <RepositoryDataTable
                  ref={dataTableRef}
                  tokenStatus={tokenStatus.status}
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="local">
          <LocalRepoOnboardingForm />
        </TabsContent>
      </Tabs>

      <GitHubTokenPopup
        open={showTokenPopup}
        onClose={() => {
          console.log("[OnboardingPage] Token popup closed");
          setIsPopupOpen(false);
        }}
        onSuccess={async () => {
          await handleTokenSuccess();
          setIsPopupOpen(false);
        }}
      />
    </div>
  );
}