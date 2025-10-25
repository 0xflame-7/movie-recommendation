import { Switch, Route, Redirect } from "wouter";
import { Header } from "@/components/layout/header";
import useAuth from "@/hooks/use-auth";
import RegisterPage from "@/pages/registerPage";
import LoginPage from "@/pages/loginPage";
import PerferencesPage from "@/pages/perferencesPage";

export default function Routes() {
  const auth = useAuth();

  return (
    <div className="w-screen h-screen overflow-hidden box-border flex flex-col bg-background text-foreground">
      <Header />
      <main className="flex-1 w-full h-full overflow-hidden box-border">
        <Switch>
          <Route path="/auth/login">
            {auth?.isAuth ? <Redirect to="/" /> : <LoginPage />}
          </Route>
          <Route path="/auth/register">
            {auth?.isAuth ? <Redirect to="/" /> : <RegisterPage />}
          </Route>
          {/* Add other routes as needed */}
          <Route path="/">
            <PerferencesPage />
          </Route>
        </Switch>
      </main>
    </div>
  );
}
