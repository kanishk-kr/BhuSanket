import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BhuSanket — Land Acquisition Intelligence Platform",
  description:
    "Predictive intelligence overlay for early detection of delays in land acquisition projects. Ministry of Rural Development, Department of Land Resources.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light">
      <body className="antialiased gradient-mesh min-h-screen">
        {children}
      </body>
    </html>
  );
}
