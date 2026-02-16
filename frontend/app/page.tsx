"use client"

import { useState } from "react"

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const handleUpload = async () => {
    if (!file) {
      alert("Please upload a resume first")
      return
    }

    setLoading(true)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch("http://127.0.0.1:8001/recommend-from-resume", {
        method: "POST",
        body: formData,
      })

      const data = await response.json()
      setResults(data.results)
    } catch (error) {
      alert("Something went wrong. Check backend.")
    }

    setLoading(false)
  }

  return (
    <main className="min-h-screen bg-gray-100 flex flex-col items-center p-10">

      <h1 className="text-4xl font-bold mb-8 text-blue-700">
        🚀 GenAI Job Recommender
      </h1>

      {/* Upload Card */}
      <div className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-2xl text-center">

        <h2 className="text-xl font-semibold mb-4 text-gray-800">
          Upload Your Resume (PDF)
        </h2>

        <div className="flex items-center justify-center gap-4 mb-4">
          <label className="bg-gray-200 px-4 py-2 rounded-lg cursor-pointer hover:bg-gray-300 transition">
            📄 Choose File
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="hidden"
            />
          </label>

          {file && (
            <span className="text-sm text-gray-600">
              {file.name}
            </span>
          )}
        </div>

        <button
          onClick={handleUpload}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          {loading ? "Analyzing Resume..." : "Upload & Get Jobs"}
        </button>
      </div>

      {/* Results Section */}
      {results.length > 0 && (
        <div className="mt-12 w-full max-w-4xl">

          <h2 className="text-2xl font-bold mb-6">
            Top Recommended Jobs 🔥
          </h2>

          {results.map((job, index) => (
            <div
              key={index}
              className="bg-white p-6 mb-6 rounded-2xl shadow-md"
            >

              <div className="flex justify-between items-start">

                <div>
                  <h3 className="text-xl font-bold text-gray-800">
                    {job.title}
                  </h3>

                  <p className="text-gray-600 font-medium">
                    {job.company}
                  </p>

                  <p className="text-sm text-gray-500">
                    {job.location || "Location not specified"}
                  </p>

                  {/* Match Score */}
                  <p className="mt-2 text-sm font-semibold text-blue-600">
                    🎯 AI Match Score: {job.match_score}%
                  </p>

                  {/* Skills */}
                  <div className="mt-3 flex flex-wrap gap-2">
                    {job.skills_detected?.map((skill: string, i: number) => (
                      <span
                        key={i}
                        className="bg-blue-100 text-blue-700 px-3 py-1 text-xs rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>

                </div>

                {/* Apply Button */}
                <a
                  href={job.apply_link}
                  target="_blank"
                  className="bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 transition"
                >
                  Apply
                </a>

              </div>
            </div>
          ))}
        </div>
      )}

    </main>
  )
}
