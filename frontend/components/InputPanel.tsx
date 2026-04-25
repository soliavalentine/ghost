"use client";
import { useCallback, useState } from "react";

type Props = {
  onSubmit: (fd: FormData) => void;
  loading: boolean;
};

export default function InputPanel({ onSubmit, loading }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [jobDesc, setJobDesc] = useState("");
  const [name, setName] = useState("");
  const [gender, setGender] = useState("male");
  const [dragActive, setDragActive] = useState(false);

  const setValidPdf = useCallback((f: File | null | undefined) => {
    if (f && (f.type === "application/pdf" || f.name.endsWith(".pdf"))) {
      setFile(f);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragActive(false);
      setValidPdf(e.dataTransfer.files[0]);
    },
    [setValidPdf]
  );

  const canSubmit =
    !!file &&
    jobDesc.trim().length >= 20 &&
    name.trim().split(/\s+/).length >= 2 &&
    !loading;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit || !file) return;
    const fd = new FormData();
    fd.append("resume", file);
    fd.append("job_description", jobDesc.trim());
    fd.append("applicant_name", name.trim());
    fd.append("gender", gender);
    onSubmit(fd);
  };

  return (
    <div className="sticky top-8">
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Resume upload */}
        <div>
          <label className="block text-xs font-mono text-zinc-500 uppercase tracking-widest mb-2">
            Resume (PDF)
          </label>
          <div
            role="button"
            tabIndex={0}
            className={`border border-dashed rounded-lg p-5 text-center cursor-pointer transition-colors select-none ${
              dragActive
                ? "border-zinc-400 bg-zinc-900"
                : file
                ? "border-zinc-600 bg-zinc-900/50"
                : "border-zinc-800 hover:border-zinc-700"
            }`}
            onDragEnter={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() =>
              document.getElementById("resume-file-input")?.click()
            }
            onKeyDown={(e) =>
              e.key === "Enter" &&
              document.getElementById("resume-file-input")?.click()
            }
          >
            <input
              id="resume-file-input"
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              onChange={(e) => setValidPdf(e.target.files?.[0])}
            />
            {file ? (
              <div>
                <div className="text-sm font-mono text-white truncate">
                  {file.name}
                </div>
                <div className="text-xs font-mono text-zinc-600 mt-1">
                  {(file.size / 1024).toFixed(0)} KB ·{" "}
                  <span
                    className="text-zinc-500 hover:text-white underline cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                    }}
                  >
                    remove
                  </span>
                </div>
              </div>
            ) : (
              <div>
                <div className="text-sm text-zinc-500 font-mono">
                  Drop PDF or click to upload
                </div>
                <div className="text-xs text-zinc-700 font-mono mt-1">
                  Max 10 MB
                </div>
              </div>
            )}
          </div>
          <div className="text-xs font-mono text-zinc-700 mt-2">
            Your resume is processed in memory and never stored.
          </div>
        </div>

        {/* Full name */}
        <div>
          <label className="block text-xs font-mono text-zinc-500 uppercase tracking-widest mb-2">
            Full Name
          </label>
          <input
            type="text"
            placeholder="First Last"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2.5 text-sm font-mono text-white placeholder-zinc-700 focus:outline-none focus:border-zinc-600 transition-colors"
          />
          <div className="text-xs font-mono text-zinc-700 mt-1">
            Used to generate name variants for comparison
          </div>
        </div>

        {/* Gender */}
        <div>
          <label className="block text-xs font-mono text-zinc-500 uppercase tracking-widest mb-2">
            Gender{" "}
            <span className="text-zinc-700 normal-case tracking-normal font-sans">
              (selects which name variant set to use)
            </span>
          </label>
          <div className="flex gap-2">
            {(["male", "female", "nonbinary"] as const).map((g) => (
              <button
                key={g}
                type="button"
                onClick={() => setGender(g)}
                className={`flex-1 py-2 text-xs font-mono rounded-lg border transition-colors ${
                  gender === g
                    ? "border-zinc-400 text-white bg-zinc-800"
                    : "border-zinc-800 text-zinc-600 hover:border-zinc-700 hover:text-zinc-400"
                }`}
              >
                {g}
              </button>
            ))}
          </div>
        </div>

        {/* Job description */}
        <div>
          <label className="block text-xs font-mono text-zinc-500 uppercase tracking-widest mb-2">
            Job Description
          </label>
          <textarea
            placeholder="Paste the full job description here…"
            value={jobDesc}
            onChange={(e) => setJobDesc(e.target.value)}
            rows={12}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2.5 text-sm text-zinc-300 placeholder-zinc-700 focus:outline-none focus:border-zinc-600 resize-none transition-colors leading-relaxed"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={!canSubmit}
          className={`w-full py-3 font-mono text-sm font-bold rounded-lg border transition-all ${
            loading
              ? "border-zinc-700 text-zinc-500 cursor-wait"
              : canSubmit
              ? "border-white bg-white text-black hover:bg-zinc-100 cursor-pointer"
              : "border-zinc-800 text-zinc-700 cursor-not-allowed"
          }`}
        >
          {loading ? "RUNNING AUDIT…" : "RUN AUDIT →"}
        </button>
      </form>
    </div>
  );
}
