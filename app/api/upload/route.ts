import { NextRequest } from "next/server";
import { writeFile } from "fs/promises";
import { join } from "path";
import { mkdir } from "fs/promises";

const UPLOAD_DIR = join(process.cwd(), "uploads");
const MAX_FILE_SIZE = 5 * 1024 * 1024;

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

    // const formData = await request.formData();
    let formData;
    try {
      formData = await request.formData();
    } catch (err) {
      console.error("Failed to parse form data:", err);
      return new Response(
        JSON.stringify({ error: "Invalid form data or network interruption" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    const files = formData.getAll("files");
    if (!files || files.length === 0) {
      return new Response(
        JSON.stringify({ error: "No files provided in the upload request" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
    
    const encoder = new TextEncoder();

    const stream = new TransformStream();
    const writer = stream.writable.getWriter();

    const abortController = new AbortController();
    request.signal.addEventListener("abort", () => {
      console.warn("Client aborted the request");
      abortController.abort();
    });


    const processFiles = async () => {
      const processedFiles = [];
      let processedCount = 0;

      for (const file of files) {
        
        if (!(file instanceof File)) {
          continue;
        }
        if (abortController.signal.aborted) {
          console.warn("Aborted before file:", file.name);
          break;
        }

        try {
          const filename = file.name;
          const filePath = join(UPLOAD_DIR, filename);
          const buffer = Buffer.from(await file.arrayBuffer());

          // Check file size
          if (buffer.length > MAX_FILE_SIZE) {
            processedCount++;
            processedFiles.push({
              filename,
              status: "failed",
              message: "File size exceeds limit",
            });
            await writer.write(
              encoder.encode(
                JSON.stringify({
                  type: "progress",
                  current_file: filename,
                  processed_count: processedCount,
                  total_files: files.length,
                  percent: Math.round((processedCount / files.length) * 100),
                  processed_files: [
                    ...processedFiles,
                    {
                      filename,
                      status: "completed",
                      message: "File processed but failed to upload due to size limit",
                    },
                  ],
                }) + "\n"
              )
            );
            continue;
          }

          // Save file
          await writeFile(filePath, buffer);

          // Send progress update
          processedCount++;
          const progressUpdate = {
            type: "progress",
            current_file: filename,
            processed_count: processedCount,
            total_files: files.length,
            percent: Math.round((processedCount / files.length) * 100),
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

    processFiles().catch(async (error) => {
      console.error("Processing error:", error);
    
      try {
        await writer.write(
          encoder.encode(
            JSON.stringify({
              type: "error",
              message: "Upload interrupted or failed unexpectedly",
            }) + "\n"
          )
        );
        await writer.close();
      } catch (err) {
        console.warn("Failed to write error to stream:", err);
      }
    });

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
