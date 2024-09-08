document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);


  // Compose email event
  document.querySelector("#compose-form").addEventListener('submit', send_email)

  // By default, load the inbox
  load_mailbox('inbox');
});



function compose_email(recipients = '', subject = '', body = '') {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#opened-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = recipients;
  document.querySelector('#compose-subject').value = subject;
  document.querySelector('#compose-body').value = body;
}


function send_email() {
  const data = JSON.stringify({
    recipients: document.querySelector('#compose-recipients').value,
    subject: document.querySelector('#compose-subject').value,
    body: document.querySelector('#compose-body').value
  });
  fetch('/emails', {
    method: 'POST',
    body: data
  })
  .then(response => response.json())
  .then(result => {
      load_mailbox('sent');
      return false;
  });
  return false;
}



function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#opened-email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  console.log(`/emails/${mailbox}`)
  // Load emails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Print emails
    console.log(emails);

    // ... do something else with emails ...
    emails.forEach(email => {
      read_class = email.read ? "read" : "unread"
      document.querySelector("#emails-view").innerHTML += 
        `<div class="email ${read_class}" data-id="${email.id}">
          <span><strong>${email.subject}</strong> From: ${email.sender} To: ${email.recipients} Timestamp: ${email.timestamp}</span>
        </div>`;
    });
    add_emails_event_listeners();
  });
}


function add_emails_event_listeners() {
  document.querySelectorAll('.email').forEach((email_item) => email_item.addEventListener('click', () => open_email(email_item.dataset.id)));
}


function open_email(id) {

  // Show the opened email and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#opened-email-view').style.display = 'block';

  console.log("email: " + id)
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    emailContainer = document.querySelector('#opened-email-view');
    const archive_label = email.archived ? 'Unarchive' : 'Archive';
    emailContainer.innerHTML = 
    `<h4>${email.subject}</h4>
    <button id="archive_button" class="btn btn-sm btn-outline-primary">${archive_label}</button>
    <p>
      From: ${email.sender}<br/>
      To: ${email.recipients}<br/>
      On: ${email.timestamp}
    </p>
    <hr/>
    <p>${email.body}</p>
    `;
    const replyButton = document.createElement('button');
    replyButton.value = 'Reply';
    replyButton.innerHTML = 'Reply';
    emailContainer.append(replyButton);
    body = `
    
    On ${email.timestamp} ${email.sender} wrote:
    ${email.body}`;
    replyButton.addEventListener('click', () => compose_email(email.sender, 'Re: ' + email.subject, body));
    
    const archiveButton = document.querySelector('#archive_button');
    archiveButton.addEventListener('click', () => archive_email(email.id, email.archived));
  });

  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })
}


function archive_email(id, archived) {
  const new_archived_status = !archived;
  const archive_label = new_archived_status ? 'Unarchive' : 'Archive';
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: new_archived_status
    })
  })
  .then(response => {
    document.querySelector('#archive_button').innerHTML = archive_label;
  })
}
