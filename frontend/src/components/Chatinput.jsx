export default function ChatInput({ value, setValue, send }) {
  return (
    <div className="p-4 border-t border-[#1f2a44] bg-[#0f1424]">
      <div className="flex gap-2">
        <input
          className="flex-1 bg-[#0b0f19] border border-[#2a3555] rounded-xl p-3"
          placeholder="Ask about the research paper..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />

        <button
          onClick={send}
          className="bg-purple-600 px-5 rounded-xl"
        >
          Send
        </button>
      </div>
    </div>
  )
}
