import Link from "next/link";

export default function HeroSection() {
  return (
    <section className="bg-gradient-to-b from-blue-50 to-white py-20 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Extract Structured Data from PDFs with AI
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Upload your PDF or image files and get structured Excel output in seconds.
          Powered by advanced AI vision models.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/tool/pdf-to-excel"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Try Now
          </Link>
          <Link
            href="/about"
            className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            Learn More
          </Link>
        </div>
      </div>
    </section>
  );
}
