import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Đối thoại Lịch Sử Việt Nam",
  description: "Gặp gỡ và đối thoại cùng các nhân vật lịch sử vĩ đại của Việt Nam",
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
        <link
          href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Cinzel+Decorative:wght@400;700;900&family=Noto+Serif:ital,wght@0,400;0,600;0,700;1,400;1,600&family=IM+Fell+English+SC&family=Be+Vietnam+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
