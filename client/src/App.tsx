import { ThemeProvider } from "next-themes";
import Routes from "./routes/routes";
import AuthProvider from "./providers/authProvider";
import { Toaster } from "sonner";

function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem={true}>
      <AuthProvider>
        <Toaster position="bottom-right" />
        <Routes />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
