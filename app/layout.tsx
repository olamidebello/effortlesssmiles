import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Effortless Smiles | Your signature sparkle",
  description: "Tooth gems, whitening, and smile essentials. Your smile. Your signature sparkle.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
