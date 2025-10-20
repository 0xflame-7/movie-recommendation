import { ThemeProvider } from "next-themes";
import Routes from "./routes/routes";

function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem={true}>
      <Routes />
    </ThemeProvider>
  );
}

export default App;
