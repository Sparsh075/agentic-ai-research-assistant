export default function Sidebar({ docLoaded }) {
  return (
    <div className="w-72 bg-[#0f1424] border-r border-[#1f2a44] p-5">
      <h1 className="text-xl font-semibold mb-6">Research AI</h1>

      {docLoaded && (
        <div className="bg-green-900/30 border border-green-700 p-3 rounded-xl">
          Document Loaded
        </div>
      )}

      <button className="mt-4 w-full border border-[#2a3555] p-2 rounded-lg hover:bg-[#18203a]">
        Upload PDF
      </button>
    </div>
  )
}
