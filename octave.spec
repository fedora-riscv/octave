%define __libtoolize /bin/true

Name:           octave
Version:        2.1.71
Release:        3%{?dist}
Summary:        A high-level language for numerical computations
Epoch:          6

Group:          Applications/Engineering
License:        GPL
Source:         ftp://ftp.octave.org/pub/octave/bleeding-edge/octave-%{version}.tar.bz2
Patch0:         octave-2.1.71-save.patch
URL:            http://www.octave.org
Requires:       gnuplot less info texinfo 
Requires:       /sbin/install-info
BuildPrereq:    gnuplot bison flex less tetex gcc-c++ gcc-gfortran lapack blas 
BuildPrereq:    ncurses-devel zlib-devel libtermcap-devel libstdc++-devel
BuildPrereq:    readline-devel glibc-devel fftw3-devel autoconf gperf
Prereq:         /sbin/ldconfig
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:       /etc/ld.so.conf.d
ExcludeArch:    ppc64 s390x

%description
GNU Octave is a high-level language, primarily intended for numerical
computations. It provides a convenient command line interface for
solving linear and nonlinear problems numerically, and for performing
other numerical experiments using a language that is mostly compatible
with Matlab. It may also be used as a batch-oriented language. Octave
has extensive tools for solving common numerical linear algebra
problems, finding the roots of nonlinear equations, integrating
ordinary functions, manipulating polynomials, and integrating ordinary
differential and differential-algebraic equations. It is easily
extensible and customizable via user-defined functions written in
Octave's own language, or using dynamically loaded modules written in
C++, C, Fortran, or other languages.


%package devel
Summary:        Development headers and files for Octave
Group:          Development/Libraries

%description devel
The octave-devel package contains files needed for developing
applications which use GNU Octave.


%prep
%setup -q
%patch0 -p0
./autogen.sh


%ifarch s390
(cd readline && libtoolize --copy --force)
(cd glob && libtoolize --copy --force)
(cd kpathsea && libtoolize --copy --force)
%endif

%build
LC_ALL=POSIX
export LC_ALL
%configure --enable-shared=yes --enable-static=no --enable-lite-kernel
make %{?_smp_mflags}


#empty
rm -f interpreter/octave.{ky,pg,tp}

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall
rm -f doc/interpreter/munge-texi doc/interpreter/*.o
strip $RPM_BUILD_ROOT/usr/libexec/octave/%{version}/oct/*/*.oct

# Make library links
mkdir -p $RPM_BUILD_ROOT/etc/ld.so.conf.d
echo "%{_libdir}/octave-%{version}" > $RPM_BUILD_ROOT/etc/ld.so.conf.d/octave-%{_arch}.conf

perl -pi -e "s,$RPM_BUILD_ROOT,," $RPM_BUILD_ROOT/%{_libexecdir}/%{name}/ls-R
perl -pi -e "s,$RPM_BUILD_ROOT,," $RPM_BUILD_ROOT/%{_datadir}/%{name}/ls-R


# XXX Nuke unpackaged files
rm -f ${RPM_BUILD_ROOT}%{_infodir}/dir

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/install-info --info-dir=%{_infodir}/ --section="Programming:" --entry="* Octave:(octave).		Interactive language for numerical computations." %{_infodir}/octave.info.gz

%preun
if [ "$1" = "0" ]; then
   /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/octave.info.gz
fi


%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc COPYING NEWS* PROJECTS README* ROADMAP SENDING-PATCHES
%doc THANKS
%doc doc/faq doc/liboctave doc/refcard emacs examples
%{_bindir}/octave
%{_bindir}/octave-%{version}
/etc/ld.so.conf.d/*
%{_libdir}/octave*
%{_datadir}/octave
%{_libexecdir}/octave/%{version}
%{_libexecdir}/octave/site
%{_mandir}/man*/octave*
%{_infodir}/octave.info*

%files devel
%defattr(-,root,root)
%{_bindir}/mkoctfile*
%{_bindir}/octave-bug*
%{_bindir}/octave-config*
%{_includedir}/octave*
%{_mandir}/man*/mkoctfile*
%{_libexecdir}/octave/ls-R


%changelog
* Fri May 27 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-3
- Added patch for http://www.octave.org/mailing-lists/bug-octave/2005/617 

* Thu May 26 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-2
- Added dist tag.

* Fri May 20 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-1
- Imported 2.1.71 from upstream, removed 2.1.70 patches (in upstream).
- Begin cleanup of spec file, including the big configure command
  (some options are obsolete, others appear unneeded if rpm configure
  macro is used).

* Mon May  3 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.70-1
- Imported 2.1.70 from upstream, removed old patches (resolved in new version)
- Changed g77 dependency to gfortran.
- Added fftw3 to BuildRequires.
- Added patches (from maintainer) to fix build problems.

* Wed Feb 23 2005 Ivana Varekova <varekova@redhat.com> 2.1.57-13
- fix typo in spec 149420

* Mon Feb 21 2005 Ivana Varekova <varekova@redhat.com> 2.1.57-12
- Fix problem with symlinks using ldconfig (bug 147922)

* Wed Feb 16 2005 Ivana Varekova <varekova@redhat.com> 2.1.57-11
- add $RPM_OPT_FLAGS

* Tue Feb 15 2005 Ivana Varekova <varekova@redhat.com> 2.1.57-10
- Fix bug 142477 - problem with signbit definition (Patch2) 

* Wed Jan 19 2005 Ivana Varekova <varekova@redhat.com> 2.1.57-9
- Fix bug #142440 - change octave.spec: autoconf is BuildPrereq
- Fix bug #142631 - change octave.spec: mkoctfile.1.gz is part of octave-devel not octave

* Wed Jan 12 2005 Tim Waugh <twaugh@redhat.com> 2.1.57-8
- Rebuilt for new readline.

* Mon Oct 18 2004 Lon Hohberger <lhh@redhat.com> 2.1.57-7
- Don't forget default attributes for -devel package

* Mon Oct 18 2004 Lon Hohberger <lhh@redhat.com> 2.1.57-6
- Remove old lib/lib64 badness.

* Wed Oct 13 2004 Lon Hohberger <lhh@redhat.com> 2.1.57-5
- Split into octave and octave-devel

* Thu Jun 24 2004 Lon Hohberger <lhh@redhat.com> 2.1.57-4
- Remove RPM_BUILD_ROOT from preun section (#119112)

* Thu Jun 24 2004 Lon Hohberger <lhh@redhat.com> 2.1.57-3
- Er, typo in patch (thanks Nils)

* Thu Jun 24 2004 Lon Hohberger <lhh@redhat.com> 2.1.57-2
- Fix for #113852 - signbit broken

* Wed Jun 15 2004 Lon Hohberger <lhh@redhat.com> 2.1.57-1
- Import 2.1.57 from upstream; this fixes #126074

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 30 2004 Karsten Hopp <karsten@redhat.de> 2.1.50-9 
- remove builddir references from file list (#119112)

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Sep 26 2003 Lon Hohberger <lhh@redhat.com> 2.1.50-7
- Add requirement for texinfo. #101299, round 3!

* Tue Sep 09 2003 Lon Hohberger <lhh@redhat.com> 2.1.50-6
- Disable s390x again

* Tue Sep 09 2003 Lon Hohberger <lhh@redhat.com> 2.1.50-5
- Disable ppc64

* Tue Sep 09 2003 Lon Hohberger <lhh@redhat.com> 2.1.50-4
- Rebuild for Taroon

* Wed Jul 30 2003 Lon Hohberger <lhh@redhat.com> 2.1.50-3
- Fix for Bugzilla #101299, round 2.  Include a patch to
quell sterr from info; it gives us funny messages if $HOME/.info
does not exist.

* Wed Jul 30 2003 Lon Hohberger <lhh@redhat.com> 2.1.50-2
- Fix for Bugzilla #101299

* Mon Jun 30 2003 Lon Hohberger <lhh@redhat.com> 2.1.50-1
- Import 2.1.50 from upstream
- Fix for Bugzilla #100682; try ppc64 again

* Mon Jun 30 2003 Lon Hohberger <lhh@redhat.com> 2.1.49-6
- Rebuild; disabling ppc64

* Mon Jun 30 2003 Lon Hohberger <lhh@redhat.com> 2.1.49-4
- Added link generation to /usr/lib so that munging
/etc/ld.so.conf isn't required to get octave to work.
(#98226)

* Thu Jun 05 2003 Lon Hohberger <lhh@redhat.com> 2.1.49-2
- Import from upstream; rebuild

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Apr 16 2003 Lon Hohberger <lhh@redhat.com> 2.1.46-2
- Rebuilt

* Tue Apr 15 2003 Lon Hohberger <lhh@redhat.com> 2.1.46-1
- Import from upstream: 2.1.46.  Disabled s390x.

* Mon Mar 10 2003 Lon Hohberger <lhh@redhat.com> 2.1.40-5
- Enabled s390[x]

* Fri Feb 7 2003 Lon Hohberger <lhh@redhat.com> 2.1.40-4
- Disabled s390 and s390x builds for now.

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Thu Jan 2 2003 Lon Hohberger <lhh@redhat.com> 2.1.40-2
- Fixed readline-devel build-rereq line. (#80673)

* Sun Nov 24 2002 Jeff Johnson <jbj@redhat.com> 2.1.40-1
- update to 2.1.40, fix matrix plotting (#77906).

* Mon Nov 11 2002 Jeff Johnson <jbj@redhat.com> 2.1.39-2
- build on x86_64.

* Sun Nov 10 2002 Jeff Johnson <jbj@redhat.com> 2.1.39-1
- update to 2.1.39.

* Sat Aug 10 2002 Elliot Lee <sopwith@redhat.com>
- rebuilt with gcc-3.2 (we hope)

* Mon Aug  5 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.1.36-7
- Rebuild

* Tue Jul 23 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.1.36-6
- Rebuild

* Thu Jul 11 2002 Trond Eivind Glomsrød <teg@redhat.com>
- Rebuild with new readline

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri Jun 14 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.1.36-3
- Get rid of 0 size doc files (#66116)

* Thu May 23 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.1.36-2
- Rebuild
- Patch C++ code gcc changed its opinion of the last 3 weeks

* Wed May  1 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.1.36-1
- 2.1.36
- Disable patch

* Wed Feb 27 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.1.35-4
- Rebuild

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue Nov 27 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.1.35-2
- Add patch for kpathsea to avoid segfaults

* Tue Nov  6 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.1.35-1
- 2.1.35
- s/Copyright/License/

* Wed Sep 12 2001 Tim Powers <timp@redhat.com>
- rebuild with new gcc and binutils

* Wed Jun 20 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Add more dependencies in BuildPrereq (#45184)

* Fri Jun 08 2001 Trond Eivind Glomsrød <teg@redhat.com>
- No longer exclude ia64

* Mon Apr 23 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.1.34

* Tue Mar 27 2001 Trond Eivind Glomsrød <teg@redhat.com>
- set LC_ALL to POSIX before building, otherwise the generated paths.h is bad

* Wed Jan 10 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.1.33

* Mon Jan 08 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- do not require compat-egcs-c++, but gcc-c++
- add some libtoolize calls to add newest versions

* Fri Dec 15 2000 Trond Eivind Glomsrød <teg@redhat.com>
- 2.1.32, no longer use CVS as our needed fixes are in now
- add Prereq for info

* Thu Dec 07 2000 Trond Eivind Glomsrød <teg@redhat.com>
- use a development version, as they have now been fixed
  to compile with the our current toolchain.

* Thu Aug 24 2000 Trond Eivind Glomsrød <teg@redhat.com>
- 2.0.16, with compat C++ compiler and new C and f77 compilers
  The C++ code is too broken for our new toolchain (C++ reserved
  words used as enums and function names, arcane macros), but
  plotting works here and not in the beta (#16759)
- add epoch to upgrade the betas

* Tue Jul 25 2000 Jakub Jelinek <jakub@redhat.com>
- make sure #line commands are not output within macro arguments

* Wed Jul 19 2000 Trond Eivind Glomsrød <teg@redhat.com>
- 2.1.31

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Thu Jul 06 2000 Trond Eivind Glomsrød <teg@redhat.com>
- no longer disable optimizations, sparc excepted

* Tue Jul  4 2000 Jakub Jelinek <jakub@redhat.com>
- Rebuild with new C++

* Mon Jul  3 2000 Matt Wilson <msw@redhat.com>
- added missing %% before {_infodir} in the %%post 

* Sat Jun 09 2000 Trond Eivind Glomsrød <teg@redhat.com>
- 2.1.30 - the old version contains invalid C++ code
  accepted by older compilers.

* Sat Jun 09 2000 Trond Eivind Glomsrød <teg@redhat.com>
- disable optimization for C++ code

* Fri Jun 08 2000 Trond Eivind Glomsrød <teg@redhat.com>
- add "Excludearch: " for Alpha - it triggers compiler bugs

* Fri Jun 08 2000 Trond Eivind Glomsrød <teg@redhat.com>
- use %%configure, %%makeinstall, %{_infodir}. %{_mandir}
- remove prefix

* Tue May 09 2000 Trond Eivind Glomsrød <teg@redhat.com>
- upgraded to 2.0.16
- removed "--enable-g77" from the configure flags - let autoconf find it

* Thu Jan 20 2000 Tim Powers <timp@redhat.com>
- bzipped source to conserve space.

* Thu Jan 13 2000 Jeff Johnson <jbj@redhat.com>
- update to 2.0.15.

* Tue Jul 20 1999 Tim Powers <timp@redhat.com>
- rebuit for 6.1

* Wed Apr 28 1999 Jeff Johnson <jbj@redhat.com>
- update to 2.0.14.

* Fri Oct 23 1998 Jeff Johnson <jbj@redhat.com>
- update to 2.0.13.90

* Thu Jul  9 1998 Jeff Johnson <jbj@redhat.com>
- repackage in powertools.

* Thu Jun 11 1998 Andrew Veliath <andrewtv@usa.net>
- Add %attr, build as user.

* Mon Jun 1 1998 Andrew Veliath <andrewtv@usa.net>
- Add BuildRoot, installinfo, require gnuplot, description from
  Octave's web page, update to Octave 2.0.13.
- Adapt from existing spec file.

* Tue Dec  2 1997 Otto Hammersmith <otto@redhat.com>
- removed libreadline stuff from the file list

* Mon Nov 24 1997 Otto Hammersmith <otto@redhat.com>
- changed configure command to put things in $RPM_ARCH-rehat-linux, 
  rather than genereated one... was causing problems between building 
  on i686 build machine.

* Mon Nov 17 1997 Otto Hammersmith <otto@redhat.com>
- moved buildroot from /tmp to /var/tmp

* Mon Sep 22 1997 Mike Wangsmo <wanger@redhat.com>
- Upgraded to version 2.0.9 and built for glibc system

* Thu May 01 1997 Michael Fulbright <msf@redhat.com>
- Updated to version 2.0.5 and changed to build using a BuildRoot
