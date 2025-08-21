const express = require("express");
const nodemailer = require("nodemailer");
require("dotenv").config();

const app = express();
app.use(express.json({ limit: "20mb" }));

// 1. Configure Nodemailer Transporter
const transporter = nodemailer.createTransport({
	host: process.env.EMAIL_HOST,
	port: process.env.EMAIL_PORT,
	secure: false,
	auth: {
		user: process.env.EMAIL_USER,
		pass: process.env.EMAIL_PASS,
	},
});

// 2. Define the API Endpoint
app.post("/send-todo-email", async (req, res) => {
	const {
		to,
		title,
		description,
		notes,
		imageBase64,
		imageFilename,
		imageContentType,
	} = req.body;

	if (!to || !title) {
		return res
			.status(400)
			.json({ error: "Missing required fields: to, title" });
	}

	// --- FIX #1: Create the attachments array ---
	const attachments = [];
	if (imageBase64 && imageFilename) {
		attachments.push({
			filename: imageFilename,
			content: imageBase64,
			encoding: "base64",
			contentType: imageContentType,
		});
	}

	// 3. Define the email content
	const mailOptions = {
		from: `"Todo App" <no-reply@todoapp.com>`,
		to: to,
		subject: `Your Reminder: ${title}`,
		html: `
            <h1>📝 Your To-Do: ${title}</h1>
            ${
							description
								? `<p><strong>Description:</strong> ${description}</p>`
								: ""
						}
            ${notes ? `<p><strong>Notes:</strong> ${notes}</p>` : ""}
            <br>
            <p>This is an automated reminder.${
							attachments.length > 0 ? " Please see the attached image." : ""
						}</p>
        `,
		attachments: attachments,
	};

	// 4. Send the email
	try {
		const info = await transporter.sendMail(mailOptions);
		console.log("Message sent: %s", info.messageId);
		const previewUrl = nodemailer.getTestMessageUrl(info);
		if (previewUrl) {
			console.log("Preview URL: %s", previewUrl);
		}

		res.status(200).json({
			message: "Email sent successfully!",
			previewUrl: previewUrl || null,
		});
	} catch (error) {
		console.error("Error sending email:", error);
		res.status(500).json({ error: "Failed to send email." });
	}
});

// 5. Start the server
const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
	console.log(`Email microservice listening on port ${PORT}`);
});
