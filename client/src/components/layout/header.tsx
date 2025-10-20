import { Link, useLocation } from "wouter";
import { Button } from "../ui/button";
import {
  LayoutDashboard,
  LogIn,
  LogOut,
  UserPlus,
  ChevronDown,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar } from "@/components/ui/avatar";
import { ThemeToggle } from "../ui/theme-toggle";
import useAuth from "@/hooks/use-auth";

export function Header() {
  const auth = useAuth();
  const { user, isAuth, logout } = auth ?? {
    user: null,
    isAuth: false,
    logout: async () => {},
  };
  const [location, setLocation] = useLocation();

  const hideLogin = location === "/auth/login";
  const hideRegister = location === "/auth/register";

  const handleLogout = async () => {
    await logout();
    setLocation("/");
  };

  return (
    <header className="border-b">
      <div className="container mx-auto flex items-center justify-between p-4">
        <Link href="/" className="text-xl font-bold flex items-center gap-2">
          <img
            src="/logo.png"
            alt="FilmFlare"
            className="w-8 h-8 rounded-2xl"
          />
          <span>FilmFlare</span>
        </Link>

        <nav className="hidden md:flex items-center gap-2">
          <ThemeToggle />

          {isAuth ? (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/dashboard" className="flex items-center gap-1">
                  <LayoutDashboard className="size-4" />
                  Dashboard
                </Link>
              </Button>

              <Button variant="ghost" size="sm" asChild>
                <Link
                  href="/dashboard/stats"
                  className="flex items-center gap-1"
                >
                  <LayoutDashboard className="size-4" />
                  My Stats
                </Link>
              </Button>

              {!!user && (
                <div className="md:flex items-center space-x-4">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        className="flex items-center space-x-2"
                      >
                        {user?.profilePic ? (
                          <img
                            src={user.profilePic}
                            alt="Profile"
                            className="w-8 h-8 rounded-full object-cover"
                          />
                        ) : (
                          <Avatar className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center font-semibold text-gray-700 uppercase">
                            {user?.name?.[0] || "U"}
                          </Avatar>
                        )}
                        <span className="font-medium">
                          {user?.name || "User"}
                        </span>
                        <ChevronDown size={14} className="text-gray-600" />
                      </Button>
                    </DropdownMenuTrigger>

                    <DropdownMenuContent align="end" className="w-48">
                      <DropdownMenuItem
                        onClick={handleLogout}
                        className="text-danger"
                      >
                        <LogOut className="w-4 h-4 mr-2" /> Logout
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              )}
            </>
          ) : (
            <>
              {!hideLogin && (
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/auth/login" className="flex items-center gap-1">
                    <LogIn className="size-4" />
                    Login
                  </Link>
                </Button>
              )}

              {!hideRegister && (
                <Button variant="ghost" size="sm" asChild>
                  <Link
                    href="/auth/register"
                    className="flex items-center gap-1"
                  >
                    <UserPlus className="size-4" />
                    Register
                  </Link>
                </Button>
              )}
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
