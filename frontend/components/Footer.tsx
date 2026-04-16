export default function Footer() {
  return (
    <footer className="border-t-2 border-black bg-white py-6 mt-auto">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p className="font-mono text-sm font-bold uppercase text-gray-600">
          <a 
            href="http://beian.miit.gov.cn/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="hover:underline decoration-2 underline-offset-2"
          >
            京 ICP 备 2026013739 号 -2
          </a>
        </p>
        <p className="font-mono text-xs text-gray-400 mt-2 uppercase">
          对话式 openclaw 技术探索
        </p>
      </div>
    </footer>
  );
}
