import React, { useEffect, useState, useCallback } from "react"
import "tailwindcss/tailwind.css"

interface LoadingProps {
  time: number // Time in seconds until reaching 99%
}

const Loading: React.FC<LoadingProps> = ({ time }) => {
  const [progress, setProgress] = useState(0)

  const getRandomIncrement = useCallback(() => {
    // Much bigger jumps at the start
    if (progress < 30) {
      return Math.random() * 15 + 5 // 5-20% jumps in early stage
    }
    // Medium jumps in middle stage
    if (progress < 70) {
      return Math.random() * 8 + 2 // 2-10% jumps
    }
    // Smaller jumps near the end
    const remainingProgress = 99 - progress
    const maxJump = Math.max(remainingProgress / 4, 1) // Never jump less than 1%
    return Math.random() * maxJump
  }, [progress])

  const getRandomDelay = useCallback(() => {
    // Very quick updates at start
    if (progress < 30) {
      return Math.random() * 100 + 50 // 50-150ms delays
    }
    // Moderate delays in middle
    if (progress < 70) {
      return Math.random() * 200 + 100 // 100-300ms delays
    }
    // Slower towards end
    const baseDelay = (time * 1000) / 15
    const variability = baseDelay * 0.5
    return baseDelay + (Math.random() * variability - variability / 2)
  }, [time, progress])

  useEffect(() => {
    let timeoutId: NodeJS.Timeout | null = null

    const scheduleNextIncrement = () => {
      if (progress >= 99) return

      const delay = getRandomDelay()
      timeoutId = setTimeout(() => {
        setProgress((prev) => {
          const next = Math.min(prev + getRandomIncrement(), 98)
          if (next < 98) scheduleNextIncrement()
          return next
        })
      }, delay)
    }

    scheduleNextIncrement()

    // Schedule the final jump to 99% at the specified time
    const finalTimeout = setTimeout(() => {
      setProgress(99)
    }, time * 1000)

    return () => {
      if (timeoutId) clearTimeout(timeoutId)
      clearTimeout(finalTimeout)
    }
  }, [time, getRandomIncrement, getRandomDelay, progress])

  const textClass =
    progress === 99
      ? "text-lg font-medium text-gray-800"
      : "text-lg font-medium text-gray-800 animate-pulse"

  return (
    <div className="flex flex-col items-center justify-center h-fit w-48 py-2">
      <div className={textClass}>Loading... {Math.floor(progress)}%</div>
      <div className="w-3/4 h-2 bg-gray-300 rounded-full overflow-hidden mt-6">
        <div
          className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all duration-75"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  )
}

export default Loading
