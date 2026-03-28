interface MetricsBentoProps {
  karma: number
  karmaWeekly: number
  trustScore: number
}

export function MetricsBento({ karma, karmaWeekly, trustScore }: MetricsBentoProps) {
  const progress = `${trustScore}%`

  return (
    <section className="grid grid-cols-2 gap-4">
      <div className="col-span-1 bg-on-background p-4 border-2 border-black shadow-hard rounded-xl flex flex-col justify-between aspect-square">
        <span className="font-label text-[10px] font-black text-black uppercase tracking-widest">KARMA</span>
        <div className="flex flex-col">
          <span className="font-headline text-4xl font-black text-black">{karma.toLocaleString()}</span>
          <span className="font-label text-[10px] text-black/60 font-bold italic">
            +{karmaWeekly} THIS WEEK
          </span>
        </div>
      </div>

      <div className="col-span-1 bg-surface-container p-4 border-2 border-black shadow-hard rounded-xl flex flex-col items-center justify-center gap-2">
        <div
          className="circular-progress"
          style={{ '--progress': progress } as React.CSSProperties}
        >
          <div className="circular-inner">
            <span className="font-headline text-xl font-bold text-on-surface">{trustScore}%</span>
          </div>
        </div>
        <span className="font-label text-[10px] font-black uppercase tracking-widest">TRUST SCORE</span>
      </div>

    </section>
  )
}
