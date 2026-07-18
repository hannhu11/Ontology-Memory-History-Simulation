import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Nguyễn Trãi — Đối Thoại Lịch Sử Tương Tác",
  description:
    "Trải nghiệm đối thoại tương tác cùng Nguyễn Trãi và các nhân vật lịch sử Việt Nam. Mô phỏng lịch sử dựa trên AI, Ontology và bộ nhớ ký ức — dành cho giáo dục, nghiên cứu và viện bảo tàng.",
  keywords: [
    "Nguyễn Trãi",
    "lịch sử Việt Nam",
    "đối thoại lịch sử",
    "interactive storytelling",
    "AI history simulation",
    "viện bảo tàng",
    "Bình Ngô đại cáo",
  ],
  openGraph: {
    title: "Nguyễn Trãi — Đối Thoại Lịch Sử Tương Tác",
    description: "Trải nghiệm nhập vai đối thoại cùng các nhân vật lịch sử Việt Nam",
    type: "website",
  },
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="vi">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
