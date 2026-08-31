import "./globals.css";

export const metadata = { title: "FraudStream", description: "Real-time fraud operations dashboard" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

