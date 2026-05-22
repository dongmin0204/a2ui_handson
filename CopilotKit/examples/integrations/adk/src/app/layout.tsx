import type { Metadata } from "next";

import { CopilotKit } from "@copilotkit/react-core";
import "./globals.css";
import "@copilotkit/react-ui/styles.css";

export const metadata: Metadata = {
  title: "GDGoC 오픈세미나 5/22",
  description: "A2UI와 ADK + copliotkit",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className={"antialiased"}>
        <CopilotKit
          runtimeUrl="/api/copilotkit"
          agent="my_agent"
          enableInspector={false}
        >
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
