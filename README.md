# TidyMail

TidyMail is a script to automatically tidy up the formatting of both simple and multi-part MIME mail messages. It performs the following operations:

  * Normalises
  * Strips leading and trailing whitespace from the message
  * Removes quoted signatures
  * Removes everything after a line containing only "--", and replaces it with a signature

The intention is to make it easier to send well-formatted mail from clients such as iOS Mail. As such, it checks the X-Mailer header to identify those clients.

It is simply invoked as a Unix filter. Typically, this would be done automatically via and MTA such as Exim.

