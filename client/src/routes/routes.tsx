import { Switch, Route, Redirect } from "wouter";
import { Header } from "../components/layout/header";
import useAuth from "@/hooks/use-auth";
import LoginPage from "@/pages/loginPage";
import RegisterPage from "@/pages/registerPage";

export default function Routes() {
  const auth = useAuth();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <Switch>
        {/* Public routes */}
        {/* <Route path="/">
          <Landing />
        </Route> */}

        <Route path="/auth/login">
          {auth?.isAuth ? <Redirect to="/" /> : <LoginPage />}
        </Route>

        <Route path="/auth/register">
          {auth?.isAuth ? <Redirect to="/" /> : <RegisterPage />}
        </Route>

        {/* Protected route */}
        {/* <Route path="/dashboard">
          {isAuth ? <Dashboard /> : <Redirect to="/auth/login" />}
        </Route> */}

        {/* Fallback */}
        {/* <Route path="*" component={NotFound} /> */}
      </Switch>
    </div>
  );
}
