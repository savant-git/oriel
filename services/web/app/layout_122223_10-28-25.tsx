import "./../styles/globals.css";
export const metadata = { title: "Savant UI", description: "Fractal adaptive UI baseline" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gunmetal text-gold-light min-h-screen flex flex-col">
        <header className="p-4 border-b border-gold-dark flex items-center justify-between">
          <h1 className="text-2xl font-mono tracking-widest text-gold">savant</h1>
          <nav className="space-x-6 text-sm">
            <a href="#" className="hover:text-gold-light">Task Engine</a>
            <a href="#" className="hover:text-gold-light">Enhancement</a>
            <a href="#" className="hover:text-gold-light">Monitor</a>
          </nav>
        </header>
        <main className="flex-1 flex flex-col items-center justify-center">
          {children}
        </main>
        <footer className="p-4 text-xs text-gold-light/60 text-center border-t border-gold-dark">
          savant ⬢ intelligence through discipline
        </footer>
      </body>
    </html>
  );
}
