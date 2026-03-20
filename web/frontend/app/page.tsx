import Header from "@/components/header";
import HeroSection from "@/components/hero-section";
import FeatureCards from "@/components/feature-cards";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <HeroSection />
        <section className="py-16 px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-2xl font-semibold text-center mb-8 text-gray-800">
              What can you do?
            </h2>
            <FeatureCards />
          </div>
        </section>
        <section className="py-16 px-4 bg-white">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              Ready to extract your data?
            </h2>
            <p className="text-gray-600 mb-8">
              Upload your PDF or image file, configure your extraction settings, and get structured Excel output in seconds.
            </p>
            <Link
              href="/tool/pdf-to-excel"
              className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Try the Tool
            </Link>
          </div>
        </section>
      </main>
      <footer className="py-8 px-4 border-t bg-white">
        <div className="max-w-6xl mx-auto text-center text-gray-500 text-sm">
          <p>© 2024 PDF to Excel with AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
