import MessageBubble from "./MessageBubble"

export default function ChatWindow({ messages, thinking }) {
  return (
    <div className="flex-1 overflow-y-auto p-6">
      {messages.map((m, i) => (
        <MessageBubble key={i} role={m.role} text={m.text} />
      ))}

      {thinking && (
        <div className="text-gray-400 animate-pulse">
          Assistant is thinking...
        </div>
      )}
    </div>
  )
}
