# From src/version.h:#define OCTAVE_API_VERSION
%global octave_api api-v48+

# For rc versions, change release manually
#global rcver %{nil}
%if 0%{?rcver:1}
%global rctag -rc%{?rcver}
%endif

Name:           octave
Epoch:          6
Version:        3.6.4
Release:        7%{?dist}
Summary:        A high-level language for numerical computations
Group:          Applications/Engineering
License:        GPLv3+
URL:            http://www.octave.org

%if 0%{!?rcver:1}
Source0:        ftp://ftp.gnu.org/gnu/octave/octave-%{version}.tar.bz2
%else
Source0:        ftp://alpha.gnu.org/gnu/octave/octave-%{version}%{rctag}.tar.gz
%endif
# RPM macros for helping to build Octave packages
Source1:        macros.octave
# Ignore deps when doing a pkg build for now
Patch1:         octave-pkgbuilddeps.patch
# https://savannah.gnu.org/bugs/index.php?32839
# Fix building packages from directories
Patch2:         octave-3.4.0-pkgbuilddir.patch
# aarch64 support (#926264)
Patch3:         octave-aarch64.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Provides:       octave(api) = %{octave_api}
Provides:       bundled(gnulib)

BuildRequires:  bison flex less gcc-gfortran
%ifnarch %{arm}
BuildRequires:  atlas-devel 
%else
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
%endif
BuildRequires:  ncurses-devel zlib-devel hdf5-devel texinfo qhull-devel
BuildRequires:  readline-devel glibc-devel fftw-devel gperf ghostscript
BuildRequires:  curl-devel pcre-devel texinfo-tex arpack-devel libX11-devel
BuildRequires:  suitesparse-devel glpk-devel gnuplot desktop-file-utils
BuildRequires:  GraphicsMagick-c++-devel fltk-devel ftgl-devel qrupdate-devel
BuildRequires:  tex(dvips) mesa-libGL-devel mesa-libGLU-devel

Requires:        epstool gnuplot gnuplot-common less info texinfo 
Requires:        hdf5 = %{_hdf5_version}
Requires(post):  info
Requires(preun): info


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
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       readline-devel fftw-devel hdf5-devel zlib-devel
Requires:       atlas-devel gcc-c++ gcc-gfortran

%description devel
The octave-devel package contains files needed for developing
applications which use GNU Octave.


%package doc
Summary:        Documentation for Octave
Group:          Documentation
%if 0%{?fedora} > 10 || 0%{?rhel} > 5
BuildArch:      noarch
%endif

%description doc
This package contains documentation for Octave.

%prep
%setup -q -n %{name}-%{version}%{?rctag}
%patch1 -p1 -b .pkgbuilddeps
%patch2 -p1 -b .pkgbuilddir
%patch3 -p1 -b .aarch64

# Check permissions
find -name *.cc -exec chmod 644 {} \;

%build
%global enable64 no
export F77=gfortran
# TODO: some items appear to be bundled in libcruft.. 
#   gl2ps.c is bundled.  Anything else?
%if 0%{?fedora} >= 21
%global atlasblaslib -ltatlas
%global atlaslapacklib -ltatlas
%else
%global atlasblaslib -lf77blas -latlas
%global atlaslapacklib -llapack
%endif
%configure --enable-shared --disable-static --enable-64=%enable64 \
%ifnarch %{arm}
 --with-blas="-L%{_libdir}/atlas %{atlasblaslib}" \
 --with-lapack="-L%{_libdir}/atlas %{atlaslapacklib}" \
%endif
 --with-qrupdate \
 --with-amd --with-umfpack --with-colamd --with-ccolamd --with-cholmod \
 --with-cxsparse

# Check that octave_api is set correctly (autogenerated file)
make -C src version.h
if ! grep -q '^#define OCTAVE_API_VERSION "%{octave_api}"' src/version.h
then
  echo "octave_api variable in spec does not match src/version.h"
  exit 1
fi

# SMP make still not working in Octave 3.6.0
#make OCTAVE_RELEASE="Fedora %{version}-%{release}" %{?_smp_mflags}
make OCTAVE_RELEASE="Fedora %{version}%{?rctag}-%{release}"

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
rm -f %{buildroot}%{_infodir}/dir

# Make library links
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/octave/%{version}%{?rctag}" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/octave-%{_arch}.conf

# Remove RPM_BUILD_ROOT from ls-R files
perl -pi -e "s,%{buildroot},," %{buildroot}%{_libdir}/%{name}/ls-R
perl -pi -e "s,%{buildroot},," %{buildroot}%{_datadir}/%{name}/ls-R
# Make sure ls-R exists
touch %{buildroot}%{_datadir}/%{name}/ls-R

# Create desktop file
rm %{buildroot}%{_datadir}/applications/www.octave.org-octave.desktop
desktop-file-install --remove-category Development --add-category "Education" \
  --add-category "DataVisualization" --add-category "NumericalAnalysis" --add-category "Engineering" --add-category "Physics" \
  --dir %{buildroot}%{_datadir}/applications doc/icons/octave.desktop

# Create directories for add-on packages
HOST_TYPE=`%{buildroot}%{_bindir}/octave-config -p CANONICAL_HOST_TYPE`
mkdir -p %{buildroot}%{_libdir}/%{name}/site/oct/%{octave_api}/$HOST_TYPE
mkdir -p %{buildroot}%{_libdir}/%{name}/site/oct/$HOST_TYPE
mkdir -p %{buildroot}%{_datadir}/%{name}/packages
mkdir -p %{buildroot}%{_libdir}/%{name}/packages
touch %{buildroot}%{_datadir}/%{name}/octave_packages

# work-around broken pre-linking (bug 524493)
#install -d %{buildroot}%{_sysconfdir}/prelink.conf.d
#echo "-b %{_bindir}/octave-%{version}" > %{buildroot}%{_sysconfdir}/prelink.conf.d/octave.conf

# Fix multilib installs
for include in config defaults oct-conf
do
   mv %{buildroot}%{_includedir}/%{name}-%{version}%{?rctag}/%{name}/${include}.h \
      %{buildroot}%{_includedir}/%{name}-%{version}%{?rctag}/%{name}/${include}-%{__isa_bits}.h
   cat > %{buildroot}%{_includedir}/%{name}-%{version}%{?rctag}/%{name}/${include}.h <<EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "${include}-32.h"
#elif __WORDSIZE == 64
#include "${include}-64.h"
#else
#error "Unknown word size"
#endif
EOF
done
for script in octave-config-%{version}%{?rctag} mkoctfile-%{version}%{?rctag}
do
   mv %{buildroot}%{_bindir}/${script} %{buildroot}%{_libdir}/%{name}/%{version}%{?rctag}/${script}
   cat > %{buildroot}%{_bindir}/${script} <<EOF
#!/bin/bash
ARCH=\$(uname -m)

case \$ARCH in
x86_64 | ia64 | s390x) LIB_DIR=/usr/lib64
                       SECONDARY_LIB_DIR=/usr/lib
                       ;;
* )
                       LIB_DIR=/usr/lib
                       SECONDARY_LIB_DIR=/usr/lib64
                       ;;
esac

if [ ! -x \$LIB_DIR/%{name}/%{version}%{?rctag}/${script} ] ; then
  if [ ! -x \$SECONDARY_LIB_DIR/%{name}/%{version}%{?rctag}/${script} ] ; then
    echo "Error: \$LIB_DIR/%{name}/%{version}%{?rctag}/${script} not found"
    if [ -d \$SECONDARY_LIB_DIR ] ; then
      echo "   and \$SECONDARY_LIB_DIR/%{name}/%{version}%{?rctag}/${script} not found"
    fi
    exit 1
  fi
  LIB_DIR=\$SECONDARY_LIB_DIR
fi
exec \$LIB_DIR/%{name}/%{version}%{?rctag}/${script} "\$@"
EOF
   chmod +x %{buildroot}%{_bindir}/${script}
done
# remove timestamp from doc-cache
sed -i -e '/^# Created by Octave/d' %{buildroot}%{_datadir}/%{name}/%{version}%{?rctag}/etc/doc-cache

# rpm macros
mkdir -p %{buildroot}%{_sysconfdir}/rpm
cp -p %SOURCE1 %{buildroot}%{_sysconfdir}/rpm/

%check
make check

%clean
rm -rf %{buildroot}

%post
/sbin/ldconfig
/sbin/install-info --info-dir=%{_infodir} --section="Programming" \
        %{_infodir}/octave.info || :

%preun
if [ "$1" = "0" ]; then
   /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/octave.info || :
fi

%postun -p /sbin/ldconfig

%files
%doc AUTHORS BUGS ChangeLog COPYING NEWS README
# FIXME: Create an -emacs package that has the emacs addon
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/octave-*.conf
%{_bindir}/octave*
%{_libdir}/octave/
%{_libexecdir}/octave/
%{_mandir}/man1/octave*.1.*
%{_infodir}/liboctave.info*
%{_infodir}/octave.info*
%{_infodir}/OctaveFAQ.info*
%{_datadir}/applications/octave.desktop
# octave_packages is %ghost, so need to list everything else separately
%dir %{_datadir}/octave
%{_datadir}/octave/%{version}%{?rctag}/
%{_datadir}/octave/ls-R
%ghost %{_datadir}/octave/octave_packages
%{_datadir}/octave/packages/
%{_datadir}/octave/site/
#%{_sysconfdir}/prelink.conf.d/octave.conf

%files devel
%{_sysconfdir}/rpm/macros.octave
%{_bindir}/mkoctfile
%{_bindir}/mkoctfile-%{version}%{?rctag}
%{_includedir}/octave-%{version}%{?rctag}/
%{_mandir}/man1/mkoctfile.1.*

%files doc
%doc doc/liboctave/liboctave.html doc/liboctave/liboctave.pdf
%doc doc/faq/OctaveFAQ.pdf doc/refcard/*.pdf
%doc examples/


%changelog
* Sun Sep 22 2013 Orion Poplawski - 6:3.6.4-7
- Rebuild for atlas 3.10
- Disable atlas on arm

* Thu Sep 12 2013 Dan Horák <dan[at]danny.cz> - 6:3.6.4-6
- Rebuilt to resolve broken deps on s390(x)

* Tue Jul 30 2013 Orion Poplawski <orion@cora.nwra.com> - 6:3.6.4-5
- Rebuild for glpk 4.52.1

* Thu May 16 2013 Orion Poplawski <orion@cora.nwra.com> - 6:3.6.4-4
- Rebuild for hdf5 1.8.11

* Thu Mar 28 2013 Jaromir Capik <jcapik@redhat.com> - 6:3.6.4-3
- aarch64 support (#926264)

* Fri Mar 08 2013 Ralf Corsépius <corsepiu@fedoraproject.org> - 6:3.6.4-2
- Remove %%config from %%{_sysconfdir}/rpm/macros.*
  (https://fedorahosted.org/fpc/ticket/259).

* Sat Feb 23 2013 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.4-1
- Update to 3.6.4 final

* Tue Feb 12 2013 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.4-0.7.rc2
- Update to 3.6.4-rc2

* Tue Feb 12 2013 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.4-0.6.rc1
- Drop vendor from desktop file

* Sun Feb 03 2013 Kevin Fenzi <kevin@scrye.com> - 6:3.6.4-0.5.rc1
- Rebuild for broken deps in rawhide

* Fri Jan 4 2013 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.4-0.4.rc1
- Update to 3.6.4-rc1
- Drop gets patch

* Fri Dec 21 2012 Orion Poplawski <orion@cora.nwra.com> - 6:3.6.4-0.3.rc0
- Add patch to ignore deps when building packages for now (bug 733615)

* Wed Dec 05 2012 Orion Poplawski <orion@cora.nwra.com> - 6:3.6.4-0.2.rc0
- Restore gets patch
- Rebuild for hdf5 1.8.10

* Wed Oct 17 2012 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.4-0.1.rc0
- Update to 3.6.4-rc0
- Drop sparse patch applied upstream

* Thu Sep 6 2012 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.3-2
- Add upstream patch to fix sparse matrix test crash

* Wed Sep 5 2012 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.3-1
- Update to 3.6.3
- Drop gets patch fixed upstream

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:3.6.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jul 5 2012 Jussi Lehtola <jussilehtola@fedoraproject.org> - 6:3.6.2-2
- Build against OpenGL libraries.

* Mon Jun 4 2012 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.2-1
- Update to 3.6.2 final

* Thu May 24 2012 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.2-0.4.rc2
- Update to 3.6.2-rc2
- Add patch to update gnulib to handle gets removal

* Tue May 15 2012 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.2-0.3.rc0
- Rebuild with hdf5 1.8.9

* Tue May 15 2012 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.2-0.2.rc0
- Add Provides bundled(gnulib) (bug 821781)

* Sat May 12 2012 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.2-0.1.rc0
- Update to 3.6.2-rc0.

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:3.6.1-2
- Rebuilt for c++ ABI breakage

* Wed Feb 22 2012 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.1-1
- Update to 3.6.1.

* Thu Feb 9 2012 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.6.0-2
- Rebuild with pcre 8.30

* Sun Jan 15 2012 Jussi Lehtola <jussilehtola@fedoraproject.org> - 6:3.6.0-1
- Update to 3.6.0.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:3.4.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Nov 18 2011 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.4.3-2
- Rebuild for hdf5 1.8.8

* Mon Oct 24 2011 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.4.3-1
- Update to 3.4.3
- Drop upstreamed patches

* Wed Aug 24 2011 Jussi Lehtola <jussilehtola@fedoraproject.org> - 6:3.4.2-3
- Place rpm macros in -devel.

* Thu Aug 11 2011 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.4.2-2
- Drop smp build - seems to be failing
- Add patch to fix tar argument handling
- Add patch to fix xzip

* Sat Aug 06 2011 Jussi Lehtola <jussilehtola@fedoraproject.org> - 6:3.4.2-1
- Update to 3.4.2.

* Fri May 27 2011 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.4.0-8
- Add patch to fix Fl_File_Chooser.H location
- Add BR tex(dvips)

* Thu May 26 2011 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.4.0-7
- Rebuild for fltk 1.3.0

* Tue May 17 2011 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.4.0-6
- Rebuild for hdf5 1.8.7

* Fri Mar 18 2011 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.4.0-5
- Use libdir instead of libexecdir
- Rename octave_pkg_preun macro
- Fix multilib installs
- Re-enable prelinking, seems to work
- Add patch to enable building packages from directories

* Wed Feb 23 2011 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.4.0-4
- Update rpm macros per FPC comments

* Mon Feb 14 2011 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.4.0-3
- Add rpm macros
- Rebuild should pick up fixed suitesparse
- Disable parallel builds

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:3.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Feb 8 2011 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.4.0-1
- Update to 3.4.0
- Drop run-octave patch fixed upstream
- Add patch to support gcc 4.6

* Thu Dec 16 2010 Orion Poplawski <orion[AT]cora.nwra com> - 6:3.3.54-1
- Update to 3.3.54
- Add patch to prevent run-octave from getting installed
- Drop -DH5_USE_16_API
- Enable parallel builds
- Cleanup doc instal

* Sun Feb 28 2010 Alex Lancaster <alexlan[AT]fedoraproject org> - 6:3.2.4-3
- Temporarily disable %%check to enable build to complete and ensure
  upgrade path works.  This works around a crash in the imread.m image test 
  script, this may be the same problem as described by upstream here:
  https://www-old.cae.wisc.edu/pipermail/octave-maintainers/2010-January/014891.html

* Fri Feb 26 2010 Michal Schmidt <mschmidt@redhat.com> 6:3.2.4-2
- Fix the prelink workaround to work with any version.
- Use _sysconfdir macro instead of /etc.

* Thu Jan 28 2010 Jussi Lehtola <jussilehtola@fedoraproject.org> - 6:3.2.4-1
- Update to 3.2.4 with a few rpmlint fixes.

* Sun Jan 17 2010 Jussi Lehtola <jussilehtola@fedoraproject.org> - 6:3.2.3-4
- Fix compilation against ARPACK.

* Wed Jan 6 2010 Jussi Lehtola <jussilehtola@fedoraproject.org> - 6:3.2.3-3
- Really build against ATLAS instead of reference BLAS (#513381).

* Sun Nov 15 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 6:3.2.3-2
- Workaround broken pre-linking (#524493)

* Tue Sep 29 2009 Orion Poplawski <orion@cora.nwra.com> - 6:3.2.3-1
- Update to 3.2.3
- Re-add make check

* Tue Sep 22 2009 Rakesh Pandit <rakesh@fedoraproject.org> - 6:3.2.2-5
- Added categories to desktop file: Education, DataVisualization, NumericalAnalysis 

* Mon Sep  7 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 6:3.2.2-4
- Rebuild against new ATLAS

* Sun Sep  6 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 6:3.2.2-3
- Disable make check temporarily to get a build against newly fixed lapack

* Wed Sep 2 2009 Orion Poplawski <orion@cora.nwra.com> - 6:3.2.2-2
- Add make check

* Fri Jul 31 2009 Jussi Lehtola <jussilehtola@fedoraproject.org> - 6:3.2.2-1
- Update to latest upstream (3.2.2).

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:3.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 13 2009 Jussi Lehtola <jussilehtola@fedoraproject.org> - 6:3.2.0-2
- Added BR: ftgl-devel for native graphics.
- Dropped obsolete X-Fedora category from desktop file.
- Macro use unifications.
- Branch documentation into its own subpackage.

* Sat Jul 11 2009 Jussi Lehtola <jussilehtola@fedoraproject.org> - 6:3.2.0-1
- Update to latest upstream (3.2.0).

* Sun Apr 12 2009 Rakesh Pandit <rakesh@fedoraproject.org> - 6:3.0.5-1
- Updated to latest upstream (3.0.5)

* Mon Feb 23 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 6:3.0.3-2
- Add patches from upstream for compiling against GCC 4.4
  http://hg.savannah.gnu.org/hgweb/octave/rev/93cf10950334
  http://hg.tw-math.de/release-3-0-x/rev/712d9e045b1e

* Wed Dec 10 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 6:3.0.3-1
- Update to latest upstream (3.0.3)

* Thu Oct 23 2008 Rakesh Pandit <rakesh@fedoraproject.org> 6:3.0.2-2
- patch for sh arch: it adds '-little' flag

* Mon Sep 8 2008 Orion Poplawski <orion@cora.nwra.com> 6:3.0.2-1
- Update to 3.0.2

* Mon Apr 21 2008 Quentin Spencer <qspencer@users.sf.net> 6:3.0.1-1
- New release of octave. Remove gcc 4.3 patch.

* Mon Mar  3 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 6:3.0.0-6
- Re-enable patch, but change cstring -> string.h so it works for C as
  well as C++.  Hopefully this will #435600 for real.

* Sun Mar  2 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 6:3.0.0-5
- Backout GCC 4.3 patch temporarily, causes trouble for octave-forge and 
  may not be necessary (#435600)

* Fri Feb 29 2008 Orion Poplawski <orion@cora.nwra.com> 3.0.0-4
- Rebuild for hdf5 1.8.0 using compatability API define
- Add gcc43 patch

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 6:3.0.0-3
- Autorebuild for GCC 4.3

* Wed Jan  9 2008 Quentin Spencer <qspencer@users.sf.net> 3.0.0-2
- Add curl-devel and pcre-devel as build dependencies. Closes bug 302231.

* Fri Dec 21 2007 Quentin Spencer <qspencer@users.sf.net> 3.0.0-1
- Update to 3.0.0.

* Wed Dec 12 2007 Quentin Spencer <qspencer@users.sf.net> 2.9.19-1
- Update to 2.9.19 and update octave_api.

* Wed Dec  5 2007 Quentin Spencer <qspencer@users.sf.net> 2.9.18-1
- Update to 2.9.18 and update octave_api.

* Wed Nov 28 2007 Quentin Spencer <qspencer@users.sf.net> 2.9.17-1
- Update to 2.9.17 and update octave_api.

* Mon Nov  5 2007 Quentin Spencer <qspencer@users.sf.net> 2.9.16-1
- Update to 2.9.16, remove old patch.
- Update licencse from GPLv2+ to GPLv3+.
- Detection of glpk no longer needs special CPPFLAGS.

* Tue Oct 16 2007 Orion Poplawski <orion@ora.nwra.com> 2.9.15-2
- Updated pkg.m patch

* Mon Oct 15 2007 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.15-1
- New release. Remove old patch.

* Tue Sep 25 2007 Orion Poplawski <orion@ora.nwra.com> 2.9.14-2
- Add /usr/share/octave/packages for add on packages and %%ghost 
  /usr/share/octave/octave_packages
- Add patch for octave package manager that will be going upstream

* Tue Sep 18 2007 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.14-1
- New release.
- Remove redundant menu category in desktop file (bug 274431).
- Update license tag.
- Add qhull-devel as new build dependency.

* Thu Jul 26 2007 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.13-1
- New release.
- Changed ufsparse-devel dependency to suitesparse-devel.
- Add configure flag to close bug 245562.
- Add directories for add-on packages (bug 234012).
- Since texinfo is now separate from tetex, it is a build requirement.

* Wed May 23 2007 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.12-1
- New release.

* Tue Feb 20 2007 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.9-2
- Fix install-info bug (Bug 219404). 
- Add dependency on octave API so that breakages will be detected. (Bug 224050).
- Remove libtermcap-devel as build dependency (Bug 226768).

* Tue Oct 03 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.9-1
- New release. Remove old patch.

* Fri Sep 15 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.8-2
- Fix this bug:
  https://www.cae.wisc.edu/pipermail/bug-octave/2006-September/000687.html

* Fri Aug 25 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.8-1
- New release. Remove old patch. This fixes bug #203676.

* Tue Aug 15 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.7-3
- Add ghostscript as a build dependency.

* Tue Aug 15 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.7-2
- Update patch to fix several small bugs, including #201087.

* Fri Jul 28 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.7-1
- New release. Remove old patches and add one new one.

* Tue Jul 11 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.6-2
- Patch for some erroneous warnings and a file path bug.

* Mon Jul 10 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.6-1
- New release. Remove old patches.
- Disable 64-bit extensions (some libraries don't support 64-bit indexing yet).
- Add gcc-gfortran to -devel dependencies (mkoctfile fails without it).
- Move octave-bug and octave-config from devel to main package.
- Fix categorization of info files (bug 196760).

* Thu Apr 27 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.5-6
- Add patch for bug #190481
- Manual stripping of .oct files is no longer necessary.

* Wed Apr 19 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.5-5
- Add new patch to configure script (breaks octave-forge without it).

* Fri Mar 24 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.5-4
- Change patch again (suggested by the author on Octave mailing list).

* Fri Mar 24 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.5-3
- Fix broken patch.

* Fri Mar 24 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.5-2
- Add more changes to sparse patch.

* Thu Mar 23 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.5-1
- New upstream release; remove old patches; add sparse patch.
- Add gcc-c++ as dependency for devel package.
- Add more docs; cleanup extra files in docs.
- Simplify configure command.
- Install desktop file.

* Fri Feb 24 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.4-8
- Rebuild for new hdf5.
- Remove obsolete configure options.
- Make sure /usr/libexec/octave is owned by octave.

* Wed Feb 15 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.4-7
- Rebuild for Fedora Extras 5.

* Wed Feb  1 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.4-6
- Change dependency from fftw3 to fftw.

* Thu Jan 26 2006 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.4-5
- Rebuild for new release of hdf5.

* Mon Dec 19 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.4-4
- Rebuild for gcc 4.1.

* Thu Dec  1 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.4-3
- Make sure patch applies correctly before building!

* Thu Dec  1 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.4-2
- Patch to enable compilation on x86_64.

* Fri Nov 11 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.4-1
- New upstream release.
- Patch to make sure all headers are included in -devel.
- PKG_ADD file now needs %%{buildroot} stripped from it.
- Cleanup errors in dependencies.

* Tue Oct 25 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.3-6
- Add lapack-devel and blas-devel dependencies to devel package.

* Mon Oct 03 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.3-5
- Change umfpack-devel dependency to the new ufsparse-devel package.

* Thu Sep 22 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.3-5
- Change lapack and blas dependencies to lapack-devel and blas-devel

* Mon Aug 08 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.3-4
- Cleanup: remove redefinition of __libtoolize, ExcludeArch of two platforms,
  old s390 workarounds, and LC_ALL setting. None of these appear to be
  necessary any longer, even if the platforms were supported.
- Add --enable-64 to configure to enable 64-bit array indexing on x86_64.
- Add support for GLPK (new build dependency and CPPFLAGS for configure).

* Wed Jul 27 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.3-3
- Add fftw3-devel to dependencies for devel

* Tue Jul 26 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.3-2
- Add dependencies (hdf5-devel and zlib-devel) for devel

* Tue Jul 26 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.9.3-1
- Move to new 2.9.x development tree.
- Add umfpack-devel as new build dependency.

* Tue Jul 05 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-12
- Require hdf5-devel for build.

* Wed Jun 22 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-11
- Force octave-devel to require readline-devel.
- Add _libdir to configure command (fixes broken mkoctfile on x86_64).

* Tue Jun 21 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-10
- Add epoch to BuildRequires in octave-devel.

* Mon Jun 20 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-9
- Rebuild.

* Sat Jun 18 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-8
- Force octave-devel to require octave.

* Wed Jun  8 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-7
- Fix configure command again. The prefix isn't used for the install step
  but it is used to calculate internal variables in octave.

* Thu Jun  2 2005 Michael Schwendt <mschwendt[AT]users.sf.net> 2.1.71-6
- disable explicit gcc-c++/libstdc++-devel BR and bump for another
  rebuild attempt

* Wed Jun  1 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-4
- Fix configure command. Remove irrelevant files from docs.

* Fri May 27 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-3
- Added patch for http://www.octave.org/mailing-lists/bug-octave/2005/617 

* Thu May 26 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-2
- Added dist tag.

* Fri May 20 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.71-1
- Imported 2.1.71 from upstream, removed 2.1.70 patches (in upstream).
- Begin cleanup of spec file, including the big configure command
  (some options are obsolete, others appear unneeded if rpm configure
  macro is used).

* Tue May 03 2005 Quentin Spencer <qspencer@users.sourceforge.net> 2.1.70-1
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

* Tue Jun 15 2004 Lon Hohberger <lhh@redhat.com> 2.1.57-1
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

* Fri Jun 09 2000 Trond Eivind Glomsrød <teg@redhat.com>
- 2.1.30 - the old version contains invalid C++ code
  accepted by older compilers.

* Fri Jun 09 2000 Trond Eivind Glomsrød <teg@redhat.com>
- disable optimization for C++ code

* Thu Jun 08 2000 Trond Eivind Glomsrød <teg@redhat.com>
- add "Excludearch: " for Alpha - it triggers compiler bugs

* Thu Jun 08 2000 Trond Eivind Glomsrød <teg@redhat.com>
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
- Add %%attr, build as user.

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
