import ReactMarkdown from "react-markdown"

export default function MessageBubble({ role, text }) {
  const isUser = role === "user"

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`
          max-w-xl px-4 py-3 rounded-2xl
          ${isUser
            ? "bg-blue-600 text-white"
            : "bg-[#161c2f] border border-[#26314f]"
          }
        `}
      >
        <ReactMarkdown>{text}</ReactMarkdown>
      </div>
    </div>
  )
}
