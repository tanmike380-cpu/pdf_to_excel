export default function FeatureCards() {
  const features = [
    {
      title: "PDF & Image Support",
      description: "Upload PDF files or images (PNG, JPG) directly. No preprocessing needed.",
      icon: "📄",
    },
    {
      title: "AI-Powered Extraction",
      description: "Advanced vision models extract structured data from complex documents.",
      icon: "🤖",
    },
    {
      title: "Custom Columns",
      description: "Define your own extraction fields or use smart auto-detection.",
      icon: "📊",
    },
    {
      title: "Translation",
      description: "Automatic Chinese translation with custom terminology support.",
      icon: "🌐",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {features.map((feature, idx) => (
        <div key={idx} className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow">
          <div className="text-3xl mb-3">{feature.icon}</div>
          <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
          <p className="text-gray-600">{feature.description}</p>
        </div>
      ))}
    </div>
  );
}
