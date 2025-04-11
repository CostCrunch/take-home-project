import { NextRequest } from "next/server";
import { writeFile } from "fs/promises";
import { join } from "path";
import { mkdir } from "fs/promises";

const UPLOAD_DIR = join(process.cwd(), "uploads");

// Ensure upload directory exists
async function ensureUploadDir() {
  try {
    await mkdir(UPLOAD_DIR, { recursive: true });
  } catch (error) {
    console.error("Error creating upload directory:", error);
  }
}

export async function POST(request: NextRequest) {
  try {
    await ensureUploadDir();

    const formData = await request.formData();
    const files = formData.getAll("files");
    const encoder = new TextEncoder();

    const stream = new TransformStream();
    const writer = stream.writable.getWriter();

    const processFiles = async () => {
      const processedFiles = [];

      for (const file of files) {
        if (!(file instanceof File)) {
          continue;
        }

        try {
          const filename = file.name;
          const filePath = join(UPLOAD_DIR, filename);
          const buffer = Buffer.from(await file.arrayBuffer());

          // Save file
          await writeFile(filePath, buffer);

          // Send progress update
          const progressUpdate = {
            type: "progress",
            current_file: filename,
            total_files: files.length,
            processed_files: [
              ...processedFiles,
              {
                filename,
                status: "completed",
                message: "File processed successfully",
              },
            ],
          };

          await writer.write(
            encoder.encode(JSON.stringify(progressUpdate) + "\n")
          );

          processedFiles.push({
            filename,
            status: "completed",
            message: "File processed successfully",
          });
        } catch (error) {
          console.error("Error processing file:", error);
          processedFiles.push({
            filename: file.name,
            status: "failed",
            message: "Failed to process file",
          });
        }
      }

      // Send completion message
      const completeMessage = {
        type: "complete",
        status: "success",
        files: processedFiles,
      };

      await writer.write(
        encoder.encode(JSON.stringify(completeMessage) + "\n")
      );
      await writer.close();
    };

    processFiles().catch(console.error);

    return new Response(stream.readable, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    console.error("Upload error:", error);
    return new Response(JSON.stringify({ error: "Failed to process upload" }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }
}
