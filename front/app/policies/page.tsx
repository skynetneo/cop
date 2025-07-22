import type { Metadata } from "next";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";

// ────────────────────────────────────────────────────────────────
// Metadata  →  used by Next.js <head> for SEO & crawler directives
// ────────────────────────────────────────────────────────────────
export const metadata: Metadata = {
  title: "Privacy Policy | Accessible Solutions",
  description:
    "Learn how Accessible Solutions collects, uses, and protects your personal information, including details on our AI‑assisted services.",
  robots: {
    index: false, // privacy pages usually stay out of search results
    follow: true,
  },
};

// Tailwind container max‑width helper
const Container: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="container mx-auto px-4 md:px-8 lg:px-12 xl:px-20 py-12">
    {children}
  </div>
);

export default function PrivacyPolicyPage() {
  return (
    <main>
      <Container>
        <h1 id="top" className="text-4xl font-bold tracking-tight mb-4">
          Privacy Policy
        </h1>
        <p className="text-sm text-muted-foreground mb-8">
          Last updated: <time dateTime="2025-07-02">02 July 2025</time>
        </p>

        {/* ───── Quick‑read summary card ───── */}
        <Card className="mb-10 border-primary/30 bg-primary/5 shadow-none">
          <CardContent className="py-6 space-y-2 text-base">
            <p className="font-medium">In plain language, we:</p>
            <ul className="list-disc ml-6 space-y-1">
              <li>Collect the minimum data required to deliver and improve our Service.</li>
              <li>Never sell your personal information.</li>
              <li>Use encryption, pen‑testing, and access controls to keep data safe.</li>
              <li>Offer AI‑generated resource suggestions but never let a model make legally binding decisions.</li>
              <li>Honor your right to access, correct, or delete data we hold about you.</li>
            </ul>
          </CardContent>
        </Card>

        {/* ───── Full policy ───── */}
        <section aria-labelledby="definitions">
          <h2 id="definitions" className="text-2xl font-semibold mt-8 mb-2">
            1 Definitions
          </h2>
          <p>Capitalized terms have the meanings below:</p>
          <dl className="space-y-2">
            <dt className="font-medium">Account</dt>
            <dd>Profile that lets you access additional features.</dd>
            <dt className="font-medium">Cookies</dt>
            <dd>Small files stored on your device to remember preferences and measure usage.</dd>
            <dt className="font-medium">Personal Data</dt>
            <dd>Information that can directly or indirectly identify you.</dd>
            <dt className="font-medium">Service</dt>
            <dd>
              <Link href="https://accessiblesolutions.org" className="underline">
                accessiblesolutions.org
              </Link>{" "}
              and related experiences.
            </dd>
            <dt className="font-medium">AI Assistant</dt>
            <dd>Our secure, in‑house chat powered by large‑language models.</dd>
          </dl>
        </section>

        <section aria-labelledby="collection">
          <h2 id="collection" className="text-2xl font-semibold mt-8 mb-2">
            2 Information we collect
          </h2>
          <h3 className="text-xl font-semibold mt-6 mb-1">2.1 You provide</h3>
          <ul className="list-disc ml-6 space-y-1">
            <li>Contact details (email, phone, mailing address)</li>
            <li>Profile preferences (pronouns, language, accessibility needs)</li>
            <li>Messages &amp; uploads when chatting with our AI or staff</li>
          </ul>
          <h3 className="text-xl font-semibold mt-6 mb-1">2.2 We collect automatically</h3>
          <ul className="list-disc ml-6 space-y-1">
            <li>IP address, device type, browser
            </li>
            <li>Usage metrics (pages viewed, clicks, time spent)</li>
            <li>Error logs &amp; diagnostic data</li>
          </ul>
          <h3 className="text-xl font-semibold mt-6 mb-1">2.3 From third parties</h3>
          <p>
            If you log in with Google, Facebook, X/Twitter, or LinkedIn we receive your
            basic profile info per your settings.
          </p>
        </section>

        <section aria-labelledby="use">
          <h2 id="use" className="text-2xl font-semibold mt-8 mb-2">
            3 How we use information
          </h2>
          <ul className="list-disc ml-6 space-y-1">
            <li>Operate, maintain, and improve the Service &amp; AI Assistant</li>
            <li>Personalize content and resource suggestions</li>
            <li>Send security alerts or respond to support requests</li>
            <li>Compile de‑identified impact statistics for grants</li>
          </ul>
        </section>

        <section aria-labelledby="ai">
          <h2 id="ai" className="text-2xl font-semibold mt-8 mb-2">
            4 AI &amp; automated insights
          </h2>
          <p>
            Our AI Assistant analyzes conversations to suggest relevant services
            or auto‑populate forms. Models run on U.S. servers in an isolated
            environment. We <strong>do not</strong> use your conversations to train public models.
            Chats are deleted or anonymized after <em>18 months</em> unless you choose to keep
            them for ongoing care.
          </p>
          <p>
            The AI provides recommendations only. Human staff review any decision
            that could impact your rights (e.g., eligibility for direct aid).
            You can opt out of AI analysis in your account settings or by emailing
            <Link href="mailto:privacy@accessiblesolutions.org" className="underline">
              privacy@accessiblesolutions.org
            </Link>.
          </p>
        </section>

        <section aria-labelledby="sharing">
          <h2 id="sharing" className="text-2xl font-semibold mt-8 mb-2">
            5 When we share data
          </h2>
          <p>We share Personal Data only:</p>
          <ul className="list-disc ml-6 space-y-1">
            <li>With contract‑bound service providers (hosting, email, SMS)</li>
            <li>With partners <em>you</em> choose (e.g., local shelter referrals)</li>
            <li>For corporate restructuring (with notice to you)</li>
            <li>To comply with law or defend legal claims</li>
          </ul>
          <p>We never sell or rent your Personal Data.</p>
        </section>

        <section aria-labelledby="rights">
          <h2 id="rights" className="text-2xl font-semibold mt-8 mb-2">
            6 Your privacy rights
          </h2>
          <p>You may, at any time:</p>
          <ul className="list-disc ml-6 space-y-1">
            <li>Access or download a copy of your data</li>
            <li>Correct inaccuracies</li>
            <li>Delete your account (unless a legal duty requires retention)</li>
            <li>Opt out of marketing emails</li>
          </ul>
          <p>
            Email&nbsp;
            <Link href="mailto:privacy@accessiblesolutions.org" className="underline">
              privacy@accessiblesolutions.org
            </Link>&nbsp;and we will reply within 30 days.
          </p>
        </section>

        <section aria-labelledby="security">
          <h2 id="security" className="text-2xl font-semibold mt-8 mb-2">
            7 Security &amp; retention
          </h2>
          <p>
            We use HTTPS, encryption in transit and at rest, and regular
            penetration tests to safeguard data. Personal Data is retained only
            as long as necessary or required by law.
          </p>
        </section>

        <section aria-labelledby="children">
          <h2 id="children" className="text-2xl font-semibold mt-8 mb-2">
            8 Children’s privacy
          </h2>
          <p>
            Our Service is not directed to children under 13. If you believe we
            have inadvertently collected such data, contact us and we will delete
            it.
          </p>
        </section>

        <section aria-labelledby="changes">
          <h2 id="changes" className="text-2xl font-semibold mt-8 mb-2">
            9 Changes to this Policy
          </h2>
          <p>
            We may update this Policy to reflect changes in law or practice. We
            will post revisions here and email registered users 30 days before
            material changes take effect.
          </p>
        </section>

        <section aria-labelledby="contact">
          <h2 id="contact" className="text-2xl font-semibold mt-8 mb-2">
            10 Contact us
          </h2>
          <ul className="list-disc ml-6 space-y-1">
            <li>
              Email:&nbsp;
              <Link href="mailto:info@accessiblesolutions.org" className="underline">
                info@accessiblesolutions.org
              </Link>
            </li>
            <li>Mail: 5319 N Rocky Fork Dr, Springfield MO 65803 USA</li>
            <li>
              Web form:&nbsp;
              <Link href="/contact" className="underline">
                accessiblesolutions.org/contact
              </Link>
            </li>
          </ul>
          <p className="mt-8 text-sm">
            <Link href="#top" className="underline">
              Back to top ↑
            </Link>
          </p>
        </section>
      </Container>
    </main>
  );
}
