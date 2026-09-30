import type { Metadata } from "next";
import type { ReactNode } from "react";
import {
  Geist,
  Geist_Mono,
} from "next/font/google";

import { AppHeader } from "@/components/shell/AppHeader";
import { AppSidebar } from "@/components/shell/AppSidebar";

import "./globals.css";


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});


export const metadata: Metadata = {
  title: {
    default: "Kunora",
    template: "%s | Kunora",
  },
  description:
    "Provider-independent financial market intelligence platform.",
};


export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable}`}
    >
      <body className="bg-black text-white antialiased">
        <div className="flex min-h-screen flex-col bg-black">
          <AppHeader />

          <div className="flex flex-1">
            <AppSidebar />

            <div className="min-w-0 flex-1">
              {children}
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}