import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PET — Personal Engineering Toolkit",
  description: "Evidence-first engineering intelligence for software teams and individual builders.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
