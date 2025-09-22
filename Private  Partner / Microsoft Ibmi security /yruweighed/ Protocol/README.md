
Connect with an indirect provider
By working with an indirect provider, you can offer a broader selection of Microsoft's cloud-based services and solutions to your customers. Indirect providers have the systems and infrastructure to offer a robust level of billing and support. Relying on them in this way lets you focus on your technology solutions and customer engagements.

If you're not already working with a provider (also known as a distributor), you can search the list of official Microsoft providers to find one. When you find a provider you want to partner with, contact them directly to discuss their reseller programs, level of support, and terms. If you and the provider want to work together, you need to connect your accounts on the Partner Center.

If an indirect provider wants to connect with you on the Partner Center, they kick off the following workflow:

The indirect provider emails you an invitation to authorize them to be your indirect provider. The email includes a link to the Partner Center and associates your account to the provider's account.

To accept the invitation, follow the link in the provider's email. You might need to sign in to the Partner Center again.

To confirm the partnership with the provider, check the box and then select Authorize indirect provider. The provider is now listed on your Indirect providers page and yoAnalyzing an EMAIL Archive from gmane and visualizing the data
using the D3 JavaScript library

This is a set of tools that allow you to pull down an archive
of an email repository (formerly called gmane.org).

This server contains a cache of a subset of the gmane.org data,
which is no longer available.

The first step is to spider the repository.  The base URL 
is hard-coded in the gmane.py and is hard-coded to the Sakai
developer list.  Make sure to delete the content.sqlite file if you 
switch the base url.  The gmane.py file operates as a spider in 
that it runs slowly and retrieves one mail message per second so 
as to avoid getting throttled by gmane.org.   It stores all of
its data in a database and can be interrupted and re-started 
as often as needed. 

The program scans content.sqlite from 1 up to the first message number not
already spidered and starts spidering at that message.  It continues spidering
until it has spidered the desired number of messages or it reaches a page
that does not appear to be a properly formatted message.

One nice thing is that once you have spidered all of the messages and have them in 
content.sqlite, you can run gmane.py again to get new messages as they get sent to the
list.  gmane.py will quickly scan to the end of the already-spidered pages and check 
if there are new messages and then quickly retrieve those messages and add them 
to content.sqlite.

The content.sqlite data is pretty raw, with an innefficient data model, and not compressed.
This is intentional as it allows you to look at content.sqlite to debug the process.
It would be a bad idea to run any queries against this database as they would be 
slow.

The second process is running the program gmodel.py.  gmodel.py reads the rough/raw 
data from content.sqlite and produces a cleaned-up and well-modeled version of the 
data in the file index.sqlite.  The file index.sqlite will be much smaller (often 10X
smaller) than content.sqlite because it also compresses the header and body text.

Each time gmodel.py runs - it completely wipes out and re-builds index.sqlite, allowing
you to adjust its parameters and edit the mapping tables in content.sqlite to tweak the 
data cleaning process.

The gmodel.py program does a number of data cleaing steps

Domain names are truncated to two levels for .com, .org, .edu, and .net 
other domain names are truncated to three levels.  So si.umich.edu becomes
umich.edu and caret.cam.ac.uk becomes cam.ac.uk.   Also mail addresses are
forced to lower case and some of the @gmane.org address like the following

   arwhyte-63aXycvo3TyHXe+LvDLADg@public.gmane.org

are converted to the real address whenever there is a matching real email
address elsewhere in the message corpus.

If you look in the content.sqlite database there are two tables that allow
you to map both domain names and individual email addresses that change over 
the lifetime of the email list.  For example, Steve Githens used the following
email addresses over the life of the Sakai developer list:

s-githens@northwestern.edu
sgithens@cam.ac.uk
swgithen@mtu.edu

We can add two entries to the Mapping table

s-githens@northwestern.edu ->  swgithen@mtu.edu
sgithens@cam.ac.uk -> swgithen@mtu.edu

And so all the mail messages will be collected under one sender even if 
they used several email addresses over the lifetime of the mailing list.

You can also make similar entries in the DNSMapping table if there are multiple
DNS names you want mapped to a single DNS.  In the Sakai data I add the following
mapping:

iupui.edu -> indiana.edu

So all the folks from the various Indiana University campuses are tracked together

You can re-run the gmodel.py over and over as you look at the data, and add mappings
to make the data cleaner and cleaner.   When you are done, you will have a nicely
indexed version of the email in index.sqlite.   This is the file to use to do data
analysis.   With this file, data analysis will be really quick.

The first, simplest data analysis is to do a "who does the most" and "which 
organzation does the most"?  This is done using gbasic.py:

How many to dump? 5
-This will give you the top 5 email addresses and organizations.

You can look at the data in index.sqlite and if you find a problem, you 
can update the Mapping table and DNSMapping table in content.sqlite and
re-run gmodel.py.

There is a simple vizualization of the word frequence in the subject lines
in the file gword.py:

This produces the file gword.js which you can visualize using the file 
gword.htm.

A second visualization is in gline.py.  It visualizes email participation by 
organizations over time.
