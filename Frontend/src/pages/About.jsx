export default function About() {
  return (
    <div className="text-gray-200">
      {/* Main Content */}
      <div className="py-16 px-6 md:px-12">
        <div className="container mx-auto text-center space-y-12">
          <h1 className="text-4xl md:text-5xl font-extrabold text-indigo-500">About Us</h1>

          <p className="text-lg md:text-xl text-gray-300 max-w-4xl mx-auto">
            Our Personal Memory Question Answering system lets you explore and gain insights into your memories
            through your photos and videos. Simply upload an image, ask a question related to it, and let our AI-powered
            assistant provide answers based on the content of the image and your stored memories.
          </p>

          <div className="flex justify-center mt-10">
            <img
              src="/QA-remove.png"
              alt="Memory Question Answering"
              className="mx-auto w-48 sm:w-64 md:w-80 rounded-lg shadow-xl"
            />
          </div>

          <div className="space-y-6 mt-12">
            <h2 className="text-3xl font-semibold text-indigo-400">How It Works</h2>
            <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto">
              1. Upload your photo or video to the platform.<br />
              2. Ask any question you have about the photo or video.<br />
              3. Our intelligent assistant analyzes the content and provides relevant answers based on your image.<br />
              4. Receive insights and discover more about your memories, whether it’s the place, people, or events captured in the photo.
            </p>
          </div>

        </div>
      </div>
      <footer className="bg-gray-900 text-gray-300">
        <div className="container mx-auto text-center">
          <p>&copy; 2025 Personal Memory Q&A System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}