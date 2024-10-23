import React, { useEffect, useState } from "react"
import "tailwindcss/tailwind.css"

interface LoadingProps {
  time: number
}

const Loading: React.FC<LoadingProps> = ({ time }) => {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 99) return 99
        const increment = Math.random() * 20 // Increase randomness
        return Math.min(prev + increment, 99)
      })
    }, Math.random() * 500 + 100) // Randomize interval timing

    return () => clearInterval(interval)
  }, [time])

  useEffect(() => {
    const timeout = setTimeout(() => {
      setProgress(99)
    }, time * 1000)

    return () => clearTimeout(timeout)
  }, [time])

  return (
    <div className="flex flex-col items-center justify-center h-fit w-full py-2">
      <div className="text-xl font-medium text-gray-800 mb-6 animate-pulse">
        Loading... {Math.floor(progress)}%
      </div>
      <div className="w-3/4 h-2 bg-gray-300 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  )
}

export default Loading
