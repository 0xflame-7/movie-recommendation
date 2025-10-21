import { Switch, Route, Redirect } from "wouter";
import { Header } from "@/components/layout/header";
import useAuth from "@/hooks/use-auth";
import RegisterPage from "@/pages/registerPage";
import LoginPage from "@/pages/loginPage";

export default function Routes() {
  const auth = useAuth();

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <Header />
      <main className="flex-1">
        <Switch>
          <Route path="/auth/login">
            {auth?.isAuth ? <Redirect to="/" /> : <LoginPage />}
          </Route>
          <Route path="/auth/register">
            {auth?.isAuth ? <Redirect to="/" /> : <RegisterPage />}
          </Route>
          {/* Add other routes as needed */}
          <Route path="/">
            <div className="flex items-center justify-center min-h-[90vh]">
              <h1>Welcome to FilmFlare</h1>
            </div>
          </Route>
        </Switch>
      </main>
    </div>
  );
}
