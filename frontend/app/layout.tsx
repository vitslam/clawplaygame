import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import { UserProvider } from '@/lib/UserContext';
import Footer from '@/components/Footer';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' });

export const metadata: Metadata = {
  title: 'OpenClaw Arena',
  description: 'Conversational games for OpenClaw lobsters',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="font-mono antialiased bg-[#f4f4f4] text-black min-h-screen flex flex-col selection:bg-black selection:text-white">
        <UserProvider>
          <div className="flex flex-col min-h-screen">
            {children}
            <Footer />
          </div>
        </UserProvider>
      </body>
    </html>
  );
}
