import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Đối thoại lịch sử",
  description: "Ontology Memory History Simulation",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
