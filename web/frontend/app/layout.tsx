import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PDF to Excel with AI",
  description: "Extract structured tables from PDFs, invoices, and shipping documents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-gray-50">{children}</body>
    </html>
  );
}
