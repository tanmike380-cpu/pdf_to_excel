import Header from "@/components/header";

export default function AboutPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="py-16 px-4">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold mb-8 text-gray-900">About PDF to Excel</h1>
          
          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">What is this tool?</h2>
            <p className="text-gray-600 leading-relaxed">
              PDF to Excel with AI is an intelligent document processing tool that extracts structured data from 
              PDFs, images, and scanned documents. It uses advanced AI models to recognize and extract key 
              information from shipping documents, invoices, packing lists, and other business documents.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Use Cases</h2>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>Extract data from shipping documents and bills of lading</li>
              <li>Parse invoice details into structured spreadsheets</li>
              <li>Convert packing lists to Excel format</li>
              <li>Translate technical terms using custom terminology rules</li>
              <li>Standardize multilingual documents into a single language</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Supported File Formats</h2>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li><strong>PDF</strong> - Portable Document Format files</li>
              <li><strong>PNG, JPG, JPEG</strong> - Image files</li>
              <li><strong>TXT</strong> - Plain text files (limited support)</li>
            </ul>
            <p className="text-gray-600 mt-4">
              Maximum file size: 20MB
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Data Privacy</h2>
            <p className="text-gray-600 leading-relaxed">
              Your files are processed securely and are not stored permanently. Uploaded files and generated 
              Excel outputs are automatically deleted after 1 hour. We do not retain or share your data with 
              third parties.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">How It Works</h2>
            <ol className="list-decimal list-inside text-gray-600 space-y-2">
              <li>Upload your PDF or image file</li>
              <li>Optionally specify target columns and translation rules</li>
              <li>Click "Extract Data" to process</li>
              <li>Preview the extracted data in your browser</li>
              <li>Download the results as an Excel file</li>
            </ol>
          </section>
        </div>
      </main>
    </div>
  );
}
