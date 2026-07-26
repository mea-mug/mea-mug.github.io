# About this site

The new MEA website, built into this kit and ready to publish. For the publishing
setup (GitHub account, token, `PUBLISH.bat`), read **START-HERE.md** — that guide is
unchanged. This file only covers the website itself.

> Do not put your notes in `README.md`. It is rewritten from scratch on every publish.

---

## The pages

Six pages, in `html_files`:

| File | Live address | What it is |
|---|---|---|
| `index.html` | `/` | Home — pitch, what we do, vision, solutions, equipment preview |
| `about.html` | `/about` | Company story, mission / value / standards, the three capabilities |
| `services.html` | `/services` | The five service lines, then study → supervise → execute → advise |
| `equipment.html` | `/equipment` | 32 machines in 6 filterable families, click any photo to enlarge |
| `projects.html` | `/projects` | Photo gallery: workshop, machines built, on site, studies |
| `contact.html` | `/contact` | Form, direct details, map |

Shared files: `css/site.css` (all styling) and `js/site.js` (all behaviour). Change a
colour or a heading style once in `site.css` and every page follows.

---

## What it does

- **Dark and light mode.** Dark by default. A visitor who has never touched the switch
  follows their own computer's setting; once they click the ☀/☾ button their choice is
  remembered. Both modes are fully styled — check both after any change.
- **English and Arabic.** The ع / EN button swaps every piece of text and flips the whole
  page to right-to-left, with a proper Arabic typeface (Cairo). The choice is remembered.
- **The year updates itself.** The footer reads the real current year, so it can never go
  stale the way `© 2015` did.
- **Equipment filtering.** Six category buttons. Links like `/equipment#food` arrive
  already filtered.
- **Photo lightbox.** Click any equipment or gallery photo. Arrow keys move, Escape closes.
- Sticky header, scroll-in animations, back-to-top button, mobile menu, print stylesheet,
  and reduced-motion support for visitors who ask for less animation.

---

## Editing the text

Every translatable element holds both languages as attributes:

```html
<h3 data-en="Cranes" data-ar="رافعات">Cranes</h3>
```

Change **all three** — `data-en`, `data-ar`, and the visible text between the tags. The
visible text is what shows before the script runs and what search engines read, so it
must match `data-en`.

Form placeholders use `data-ph-en` / `data-ph-ar` the same way.

---

## Changing the contact details

They appear in the footer of all six pages plus the contact page, so use your editor's
"replace in all files":

| Find | Currently |
|---|---|
| e-mail | `info@mea-mug.com` |
| phone link | `tel:+491774648243` |
| phone shown | `+49 177 464 8243` |
| Facebook | `facebook.com/ingenieurwesen.industrie.7` |
| map coordinates | `24.6261945,46.8096092` |

**There is no street address anywhere on the site** — only a map pin, as you asked. If you
want to add one later, the contact page has a "Workshop & factory" row ready for it.

---

## The contact form

The site is plain files with no server, so the form opens the visitor's own e-mail app with
everything filled in and addressed to `info@mea-mug.com`. That works everywhere, costs
nothing, and needs no account.

To receive submissions in your inbox instead, make a free account at
<https://web3forms.com> and follow the instructions in the comment at the bottom of
`html_files/js/site.js` (section 8). It is about three lines of change.

---

## One thing to know about the addresses

Every link and image uses an address starting from the site root, like `/css/site.css` and
`/images/equipment/14-cranes.jpg`. That is correct for:

- `https://YOUR-NAME.github.io` (the kit's normal setup), and
- a custom domain such as `https://mea-mug.com`.

It would **not** work if the site were published into a sub-folder, like
`username.github.io/mea-mug/`. If you ever do that, every `/...` address needs the folder
name in front of it. Sticking to the setup in START-HERE.md avoids this entirely.

---

## The images

In `html_files/images`, grouped by section, and every one came from your old site.

- **The white borders are gone.** 29 of the photos had white margins you had added years
  ago; those have been trimmed off automatically, and the pictures now fill their frames.
- **Two sizes of everything.** The full-size file (up to 1600 px) and a `thumbs/` copy
  (up to 700 px). Grids and galleries load the thumbnail; the lightbox loads the full one.
  That is why the site stays quick despite having 70-odd photos.
- **File names describe the picture**, e.g. `equipment/26-biscuit-chips-...-wafer-biscuit.jpg`.
- Total weight is about 6 MB, down from 8.7 MB, at better quality on screen.

A few old files are deliberately **not used**: the grey divider strip, the clip-art
"e-mail / Skype / mobile" icons (replaced with clean symbols), the old Wix page background,
and one small stock photo that came from a Wix account rather than your camera. They are
still in the folder if you want them.

---

## Changes made to the old wording

You asked me to fix these, so for the record:

- **"Supplyer" → "Supplier"**, **"PROQUREMENT" → "Procurement"**, **"Alumnim" → "Aluminium"**,
  and **"concrete patch plants" → "batch plants"**.
- **"Gulf Experts" is gone.** The old About text switched to that name mid-paragraph, which
  read like leftover template copy. Everything now says **MEA** consistently, with
  **SALWA A. AL-SALEH Est.** named as the registered entity in the footer and on the contact
  page. That keeps one public brand and one legal name, which is the clearest option.
- **One e-mail instead of six**, one phone number instead of two sets.
- **The three "Our Vision / Our Services / Our Solutions" pictures were scans of text.**
  Their content is now real text on the Home and Services pages, so it can be read on a
  phone, found by Google, and translated. (The original vision scan was cut off
  mid-sentence when it was first uploaded, so its last line ends early — worth rewriting
  that paragraph when you get a chance.)

---

## Before you publish

- Decide whether `info@mea-mug.com` exists yet. If not, create it, or the form and every
  e-mail link go nowhere.
- Re-read the Home and About copy in your own voice — it is faithful to the old site, but
  the old site's English was rough in places and I have only tidied it, not rewritten it.
- Have a native Arabic reader skim the Arabic. I based it on your original Arabic where the
  old site had it, and translated the rest.
- A few photos are low-resolution Facebook-era downloads. They are the weakest thing on the
  site now; re-shooting even five or six machines would lift it a lot.

---

## Previewing on your PC before publishing

From this folder:

```bash
python scripts/build_index.py html_files _site unlisted && python -m http.server 8765 --directory _site
```

Then open <http://localhost:8765>. You must view it through this little server rather than
by double-clicking the HTML files, because of the root-relative addresses explained above.
`_site` is a throwaway build folder and is never published from your PC — GitHub rebuilds
it for you on every publish.
