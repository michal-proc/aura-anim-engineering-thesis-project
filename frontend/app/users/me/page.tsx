"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Sidebar } from "@/components/common/sidebar";
import { Header } from "@/components/common/header";
import { useI18n } from "@/lib/i18n-context";
import { useAuthStore } from "@/store/auth-store";
import { userApi } from "@/api/user";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Trash2, Lock, UserX, Save } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { FaCheck } from "react-icons/fa";

export default function UserProfilePage() {
  const router = useRouter();
  const { t } = useI18n();

  const { user, accessToken, logout, validateSession } = useAuthStore();

  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");

  useEffect(() => {
    if (user) {
      setEmail(user.email || "");
      setUsername(user.username || "");
      setFullName(user.full_name || "");
    }
  }, [user]);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);

  const [deactivatePassword, setDeactivatePassword] = useState("");
  const [deletePassword, setDeletePassword] = useState("");

  const passwordRequirements = {
    minLength: newPassword.length >= 8,
    hasUpperCase: /[A-Z]/.test(newPassword),
    hasLowerCase: /[a-z]/.test(newPassword),
    hasNumber: /[0-9]/.test(newPassword),
  };

  const isPasswordValid = Object.values(passwordRequirements).every(Boolean);

  const updateProfileMutation = useMutation({
    mutationFn: () =>
      userApi.updateProfile(
        { email, username, full_name: fullName },
        accessToken || undefined,
      ),
    onSuccess: async () => {
      toast({ title: t("profile.updateSuccess"), variant: "default" });
      // Refresh user data from backend
      await validateSession();
    },
    onError: () => {
      toast({ title: t("profile.updateError"), variant: "destructive" });
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: () =>
      userApi.changePassword(
        { current_password: currentPassword, new_password: newPassword },
        accessToken || undefined,
      ),
    onSuccess: () => {
      toast({ title: t("profile.passwordChangeSuccess"), variant: "default" });
      setPasswordDialogOpen(false);
      setTimeout(() => {
        logout();
        router.push("/login");
      }, 1500);
    },
    onError: () => {
      toast({
        title: t("profile.passwordChangeError"),
        variant: "destructive",
      });
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: () =>
      userApi.deactivateAccount(
        { password: deactivatePassword },
        accessToken || undefined,
      ),
    onSuccess: () => {
      toast({ title: t("profile.deactivateSuccess"), variant: "default" });
      logout();
      router.push("/login");
    },
    onError: () => {
      toast({ title: t("profile.deactivateError"), variant: "destructive" });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () =>
      userApi.deleteAccount(
        { password: deletePassword },
        accessToken || undefined,
      ),
    onSuccess: () => {
      toast({ title: t("profile.deleteSuccess"), variant: "default" });
      logout();
      router.push("/login");
    },
    onError: () => {
      toast({ title: t("profile.deleteError"), variant: "destructive" });
    },
  });

  const handleUpdateProfile = () => {
    updateProfileMutation.mutate();
  };

  const handleChangePassword = () => {
    if (!currentPassword) {
      toast({
        title: t("profile.currentPassword") + " is required",
        variant: "destructive",
      });
      return;
    }
    if (!newPassword) {
      toast({
        title: t("profile.newPassword") + " is required",
        variant: "destructive",
      });
      return;
    }
    if (newPassword !== confirmPassword) {
      toast({ title: t("profile.passwordMismatch"), variant: "destructive" });
      return;
    }
    if (!isPasswordValid) {
      toast({
        title: t("profile.passwordRequirementsNotMet"),
        variant: "destructive",
      });
      return;
    }
    changePasswordMutation.mutate();
  };

  const handleDeactivate = () => {
    deactivateMutation.mutate();
  };

  const handleDelete = () => {
    deleteMutation.mutate();
  };

  return (
    <ProtectedRoute>
      <div className="flex h-screen text-white">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto p-8">
            <div className="max-w-7xl mx-auto">
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent">
                {t("profile.title")}
              </h1>
              <p className="text-[#8a8aa8] mb-8">{t("profile.description")}</p>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  <Card className="bg-[#1a1a2e] border-[#2a2a4e]">
                    <CardHeader>
                      <CardTitle className="text-white">
                        {t("profile.basicInfo")}
                      </CardTitle>
                      <CardDescription className="text-[#8a8aa8]">
                        {t("profile.basicInfoDescription")}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="email" className="text-white">
                          {t("profile.email")}
                        </Label>
                        <Input
                          id="email"
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className="bg-[#0f0f1e] border-[#2a2a4e] text-white"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="username" className="text-white">
                          {t("profile.username")}
                        </Label>
                        <Input
                          id="username"
                          type="text"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          className="bg-[#0f0f1e] border-[#2a2a4e] text-white"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="fullName" className="text-white">
                          {t("profile.fullName")}
                        </Label>
                        <Input
                          id="fullName"
                          type="text"
                          value={fullName}
                          onChange={(e) => setFullName(e.target.value)}
                          className="bg-[#0f0f1e] border-[#2a2a4e] text-white"
                        />
                      </div>
                      <Button
                        onClick={handleUpdateProfile}
                        disabled={updateProfileMutation.isPending}
                        className="bg-gradient-to-r from-[#31B7EA] to-[#375DDA] hover:opacity-90 flex items-center gap-2"
                      >
                        <Save className="w-4 h-4" />
                        {t("profile.saveChanges")}
                      </Button>
                    </CardContent>
                  </Card>

                  <Card className="bg-[#1a1a2e] border-[#2a2a4e]">
                    <CardHeader>
                      <CardTitle className="text-white">
                        {t("profile.changePassword")}
                      </CardTitle>
                      <CardDescription className="text-[#8a8aa8]">
                        {t("profile.changePasswordDescription")}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Dialog
                        open={passwordDialogOpen}
                        onOpenChange={setPasswordDialogOpen}
                      >
                        <DialogTrigger asChild>
                          <Button className="bg-gradient-to-r from-[#31B7EA] to-[#375DDA] hover:opacity-90 flex items-center gap-2">
                            <Lock className="w-4 h-4" />
                            {t("profile.changePasswordButton")}
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="bg-[#1a1a2e] border-[#2a2a4e] text-white">
                          <DialogHeader>
                            <DialogTitle className="text-white">
                              {t("profile.changePassword")}
                            </DialogTitle>
                            <DialogDescription className="text-[#8a8aa8]">
                              {t("profile.changePasswordDescription")}
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4 py-4">
                            <div className="space-y-2">
                              <Label
                                htmlFor="dialogCurrentPassword"
                                className="text-white"
                              >
                                {t("profile.currentPassword")}
                              </Label>
                              <Input
                                id="dialogCurrentPassword"
                                type="password"
                                value={currentPassword}
                                onChange={(e) =>
                                  setCurrentPassword(e.target.value)
                                }
                                className="bg-[#0f0f1e] border-[#2a2a4e] text-white"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label
                                htmlFor="dialogNewPassword"
                                className="text-white"
                              >
                                {t("profile.newPassword")}
                              </Label>
                              <Input
                                id="dialogNewPassword"
                                type="password"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                className="bg-[#0f0f1e] border-[#2a2a4e] text-white"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label
                                htmlFor="dialogConfirmPassword"
                                className="text-white"
                              >
                                {t("profile.confirmPassword")}
                              </Label>
                              <Input
                                id="dialogConfirmPassword"
                                type="password"
                                value={confirmPassword}
                                onChange={(e) =>
                                  setConfirmPassword(e.target.value)
                                }
                                className="bg-[#0f0f1e] border-[#2a2a4e] text-white"
                              />
                            </div>
                            <div className="p-4 bg-[#0f0f1e] border border-[#2a2a4e] rounded-lg">
                              <p className="text-sm text-[#8a8aa8] mb-2">
                                {t("auth.passwordRequirements")}
                              </p>
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <FaCheck
                                    className={`w-4 h-4 ${passwordRequirements.minLength ? "text-green-500" : "text-gray-500"}`}
                                  />
                                  <span
                                    className={`text-sm ${passwordRequirements.minLength ? "text-green-500" : "text-gray-400"}`}
                                  >
                                    {t("auth.minLength")}
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <FaCheck
                                    className={`w-4 h-4 ${passwordRequirements.hasUpperCase ? "text-green-500" : "text-gray-500"}`}
                                  />
                                  <span
                                    className={`text-sm ${passwordRequirements.hasUpperCase ? "text-green-500" : "text-gray-400"}`}
                                  >
                                    {t("auth.hasUppercase")}
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <FaCheck
                                    className={`w-4 h-4 ${passwordRequirements.hasLowerCase ? "text-green-500" : "text-gray-500"}`}
                                  />
                                  <span
                                    className={`text-sm ${passwordRequirements.hasLowerCase ? "text-green-500" : "text-gray-400"}`}
                                  >
                                    {t("auth.hasLowercase")}
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <FaCheck
                                    className={`w-4 h-4 ${passwordRequirements.hasNumber ? "text-green-500" : "text-gray-500"}`}
                                  />
                                  <span
                                    className={`text-sm ${passwordRequirements.hasNumber ? "text-green-500" : "text-gray-400"}`}
                                  >
                                    {t("auth.hasNumber")}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                          <DialogFooter>
                            <Button
                              onClick={handleChangePassword}
                              disabled={
                                changePasswordMutation.isPending ||
                                !currentPassword ||
                                !newPassword ||
                                !confirmPassword ||
                                !isPasswordValid ||
                                newPassword !== confirmPassword
                              }
                              className="bg-gradient-to-r from-[#31B7EA] to-[#375DDA] hover:opacity-90"
                            >
                              {t("profile.changePasswordButton")}
                            </Button>
                          </DialogFooter>
                        </DialogContent>
                      </Dialog>
                    </CardContent>
                  </Card>
                </div>

                <div className="lg:col-span-1">
                  <Card className="bg-[#1a1a2e] border-[#2a2a4e]">
                    <CardHeader>
                      <CardTitle className="text-white">
                        {t("profile.actions")}
                      </CardTitle>
                      <CardDescription className="text-[#8a8aa8]">
                        {t("profile.dangerZoneDescription")}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <Separator className="bg-[#2a2a4e]" />

                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="outline"
                            className="w-full border-yellow-600 text-yellow-400 hover:bg-yellow-600/20 bg-transparent flex items-center gap-2"
                          >
                            <UserX className="w-4 h-4" />
                            {t("profile.deactivateAccount")}
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent className="bg-[#1a1a2e] border-[#2a2a4e]">
                          <AlertDialogHeader>
                            <AlertDialogTitle className="text-white">
                              {t("profile.deactivateConfirm")}
                            </AlertDialogTitle>
                            <AlertDialogDescription className="text-[#8a8aa8]">
                              {t("profile.deactivateDescription")}
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <div className="space-y-2 my-4">
                            <Label
                              htmlFor="deactivatePassword"
                              className="text-white"
                            >
                              {t("profile.confirmWithPassword")}
                            </Label>
                            <Input
                              id="deactivatePassword"
                              type="password"
                              value={deactivatePassword}
                              onChange={(e) =>
                                setDeactivatePassword(e.target.value)
                              }
                              className="bg-[#0f0f1e] border-[#2a2a4e] text-white"
                            />
                          </div>
                          <AlertDialogFooter>
                            <AlertDialogCancel className="bg-[#2a2a4e] border-[#3a3a5e] text-white">
                              {t("profile.cancel")}
                            </AlertDialogCancel>
                            <AlertDialogAction
                              onClick={handleDeactivate}
                              disabled={!deactivatePassword}
                              className="bg-yellow-600 hover:bg-yellow-700 text-white"
                            >
                              {t("profile.deactivateButton")}
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>

                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="outline"
                            className="w-full border-red-600 text-red-400 hover:bg-red-600/20 bg-transparent flex items-center gap-2"
                          >
                            <Trash2 className="w-4 h-4" />
                            {t("profile.deleteAccount")}
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent className="bg-[#1a1a2e] border-[#2a2a4e]">
                          <AlertDialogHeader>
                            <AlertDialogTitle className="text-white">
                              {t("profile.deleteConfirm")}
                            </AlertDialogTitle>
                            <AlertDialogDescription className="text-[#8a8aa8]">
                              {t("profile.deleteDescription")}
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <div className="space-y-2 my-4">
                            <Label
                              htmlFor="deletePassword"
                              className="text-white"
                            >
                              {t("profile.confirmWithPassword")}
                            </Label>
                            <Input
                              id="deletePassword"
                              type="password"
                              value={deletePassword}
                              onChange={(e) =>
                                setDeletePassword(e.target.value)
                              }
                              className="bg-[#0f0f1e] border-[#2a2a4e] text-white"
                            />
                          </div>
                          <AlertDialogFooter>
                            <AlertDialogCancel className="bg-[#2a2a4e] border-[#3a3a5e] text-white">
                              {t("profile.cancel")}
                            </AlertDialogCancel>
                            <AlertDialogAction
                              onClick={handleDelete}
                              disabled={!deletePassword}
                              className="bg-red-600 hover:bg-red-700 text-white"
                            >
                              {t("profile.deleteButton")}
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
