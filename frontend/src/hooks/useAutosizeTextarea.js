import { useLayoutEffect } from "react";

export default function useAutosizeTextarea(ref, value) {
  useLayoutEffect(() => {
    if (!ref?.current) return;
    ref.current.style.height = "0px";
    const nextHeight = Math.min(ref.current.scrollHeight, 220);
    ref.current.style.height = `${nextHeight}px`;
  }, [ref, value]);
}

