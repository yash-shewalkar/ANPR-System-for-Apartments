



// ----------------------

const nodemailer = require('nodemailer');
const fs = require('fs');

// Read the email template file
fs.readFile('email_template.html', 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading email template:', err);
        return;
    }

    // Create reusable transporter object using the default SMTP transport
    let transporter = nodemailer.createTransport({
        service: "Gmail",
        host: "smtp.gmail.com",
        port: 465,
        secure: true,
      auth: {
        user: "edi4project.22@gmail.com",
        pass: "ywtb oqld mlgi vmhu"
      }
    });

    // Define email options
    let mailOptions = {
        from: "edi4project.22@gmail.com",
        to: "iamyashshewalkar@gmail.com",
        subject: 'Test Email with Clickable Button',
        html: data // HTML content from the email template file
    };

    // Send email
    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            return console.error('Error sending email:', error);
        }
        console.log('Email sent:', info.response);
    });
});
